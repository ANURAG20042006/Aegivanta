import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.sensor import Sensor
from backend.app.core.exceptions import SentinelAIException, AuthenticationError

logger = logging.getLogger("SentinelAI.Sensor")


class SensorService:
    """Manages enrollment, heartbeats, token rotation, OTA upgrades, and fleet health."""

    @classmethod
    def _hash_token(cls, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @classmethod
    async def enroll_sensor(
        cls,
        db: AsyncSession,
        tenant_id: str,
        name: str,
        hostname: str,
        ip_address: str,
        os_type: str = "linux",
        sensor_type: str = "ENDPOINT_EDR",
        capabilities: Optional[Dict[str, Any]] = None
    ) -> Tuple[Sensor, str]:
        """Enrolls a new sensor agent and returns the Sensor model with plain enrollment token."""
        raw_token = f"sen_{secrets.token_hex(24)}"
        token_hash = cls._hash_token(raw_token)

        now = datetime.now(timezone.utc)
        sensor = Sensor(
            tenant_id=tenant_id,
            name=name,
            hostname=hostname,
            ip_address=ip_address,
            os_type=os_type,
            sensor_type=sensor_type,
            sensor_version="6.0.0",
            status="ONLINE",
            health_score=100,
            enrollment_token_hash=token_hash,
            token_expires_at=now + timedelta(days=90),
            last_token_rotation=now,
            capabilities=capabilities or {"pcap": True, "process": True, "auth": True, "compression": True},
            last_heartbeat=now
        )
        db.add(sensor)
        await db.flush()
        return sensor, raw_token

    @classmethod
    async def process_heartbeat(
        cls,
        db: AsyncSession,
        sensor_id: str,
        raw_token: str,
        telemetry_stats: Optional[Dict[str, Any]] = None
    ) -> Sensor:
        """Processes agent heartbeat and computes dynamic health score."""
        stmt = select(Sensor).where(Sensor.id == sensor_id)
        res = await db.execute(stmt)
        sensor = res.scalar_one_or_none()
        if not sensor or sensor.status == "REVOKED":
            raise AuthenticationError(detail="Sensor agent not found or revoked.")

        token_hash = cls._hash_token(raw_token)
        if sensor.enrollment_token_hash != token_hash:
            raise AuthenticationError(detail="Invalid sensor enrollment credentials.")

        now = datetime.now(timezone.utc)

        # Check token expiration
        if sensor.token_expires_at and now > sensor.token_expires_at:
            raise AuthenticationError(detail="Sensor enrollment token has expired. Rotation required.")

        sensor.status = "ONLINE"
        sensor.last_heartbeat = now

        # Health score computation
        dropped_events = telemetry_stats.get("dropped_events", 0) if telemetry_stats else 0
        queued_events = telemetry_stats.get("queued_events", 0) if telemetry_stats else 0
        sensor.offline_buffer_events = queued_events

        health = 100
        if dropped_events > 0:
            health -= min(30, dropped_events * 2)
        if queued_events > 1000:
            health -= 20
        sensor.health_score = max(10, health)

        await db.flush()
        return sensor

    @classmethod
    async def rotate_token(
        cls,
        db: AsyncSession,
        sensor_id: str,
        tenant_id: str
    ) -> Tuple[Sensor, str]:
        """Generates a new cryptographic enrollment token for the sensor."""
        stmt = select(Sensor).where(
            and_(
                Sensor.id == sensor_id,
                Sensor.tenant_id == tenant_id
            )
        )
        res = await db.execute(stmt)
        sensor = res.scalar_one_or_none()
        if not sensor or sensor.status == "REVOKED":
            raise SentinelAIException(status_code=404, detail="Active sensor not found.")

        new_raw_token = f"sen_{secrets.token_hex(24)}"
        now = datetime.now(timezone.utc)

        sensor.enrollment_token_hash = cls._hash_token(new_raw_token)
        sensor.last_token_rotation = now
        sensor.token_expires_at = now + timedelta(days=90)
        await db.flush()
        return sensor, new_raw_token

    @classmethod
    async def schedule_upgrade(
        cls,
        db: AsyncSession,
        sensor_id: str,
        tenant_id: str,
        target_version: str
    ) -> Sensor:
        """Schedules over-the-air sensor version upgrade."""
        stmt = select(Sensor).where(
            and_(
                Sensor.id == sensor_id,
                Sensor.tenant_id == tenant_id
            )
        )
        res = await db.execute(stmt)
        sensor = res.scalar_one_or_none()
        if not sensor or sensor.status == "REVOKED":
            raise SentinelAIException(status_code=404, detail="Active sensor not found.")

        sensor.target_version = target_version
        sensor.upgrade_status = "PENDING_UPGRADE"
        await db.flush()
        return sensor

    @classmethod
    async def get_fleet_health(
        cls,
        db: AsyncSession,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Calculates fleet health summary and operational metrics."""
        sensors = await cls.list_sensors(db, tenant_id)
        if not sensors:
            return {
                "total_sensors": 0,
                "online_count": 0,
                "degraded_count": 0,
                "offline_count": 0,
                "average_health_score": 100,
                "total_buffered_events": 0
            }

        now = datetime.now(timezone.utc)
        online = 0
        degraded = 0
        offline = 0
        total_health = 0
        buffered = 0

        for s in sensors:
            if s.status == "REVOKED":
                continue
            lh = s.last_heartbeat
            if isinstance(lh, str):
                try:
                    lh = datetime.fromisoformat(lh.replace("Z", "+00:00"))
                except Exception:
                    lh = now
            time_since_heartbeat = (now - lh).total_seconds()
            if time_since_heartbeat > 300:  # > 5 minutes
                s.status = "OFFLINE"
                offline += 1
            elif s.health_score < 70:
                s.status = "DEGRADED"
                degraded += 1
            else:
                online += 1


            total_health += s.health_score
            buffered += (s.offline_buffer_events or 0)

        active_count = max(1, online + degraded + offline)
        return {
            "total_sensors": len(sensors),
            "online_count": online,
            "degraded_count": degraded,
            "offline_count": offline,
            "average_health_score": round(total_health / active_count, 1),
            "total_buffered_events": buffered
        }

    @classmethod
    def get_install_command(cls, sensor_id: str, token: str, os_type: str = "linux", api_url: str = "https://app.sentinelai.io") -> Dict[str, str]:
        """Generates cross-platform one-line installation commands."""
        os_lower = os_type.lower()
        if os_lower in ["windows", "win"]:
            cmd = f'powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; iex ((New-Object System.Net.WebClient).DownloadString(\'{api_url}/scripts/install-agent.ps1\')) -SensorId \'{sensor_id}\' -Token \'{token}\' -ApiUrl \'{api_url}\'"'
        elif os_lower in ["k8s", "kubernetes"]:
            cmd = f"helm repo add aegivanta https://charts.aegivanta.io && helm install aegivanta-sensor aegivanta/sensor --set sensorId={sensor_id} --set token={token} --set apiUrl={api_url}"
        else:  # Linux systemd default
            cmd = f"curl -sSL {api_url}/scripts/install-agent.sh | sudo bash -s -- --sensor-id {sensor_id} --token {token} --api-url {api_url}"

        return {"os_type": os_type, "command": cmd}

    @classmethod
    async def list_sensors(
        cls,
        db: AsyncSession,
        tenant_id: str
    ) -> List[Sensor]:
        """Lists all enrolled sensors for a tenant."""
        stmt = select(Sensor).where(Sensor.tenant_id == tenant_id).order_by(Sensor.last_heartbeat.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def revoke_sensor(
        cls,
        db: AsyncSession,
        sensor_id: str,
        tenant_id: str,
        reason: Optional[str] = "Manual administrator revocation"
    ) -> bool:
        """Revokes a sensor agent enrollment."""
        stmt = select(Sensor).where(
            and_(
                Sensor.id == sensor_id,
                Sensor.tenant_id == tenant_id
            )
        )
        res = await db.execute(stmt)
        sensor = res.scalar_one_or_none()
        if not sensor:
            return False

        sensor.status = "REVOKED"
        sensor.revocation_reason = reason
        await db.flush()
        return True
