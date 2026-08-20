import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.sensor import Sensor
from backend.app.core.exceptions import SentinelAIException, AuthenticationError

logger = logging.getLogger("SentinelAI.Sensor")


class SensorService:
    """Manages enrollment, heartbeats, and lifecycle for customer endpoint telemetry sensors."""

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
        capabilities: Optional[Dict[str, Any]] = None
    ) -> Tuple[Sensor, str]:
        """Enrolls a new sensor agent and returns the Sensor model with plain enrollment token."""
        raw_token = f"sen_{secrets.token_hex(24)}"
        token_hash = cls._hash_token(raw_token)

        sensor = Sensor(
            tenant_id=tenant_id,
            name=name,
            hostname=hostname,
            ip_address=ip_address,
            os_type=os_type,
            status="ONLINE",
            enrollment_token_hash=token_hash,
            capabilities=capabilities or {"pcap": True, "process": True, "auth": True},
            last_heartbeat=datetime.now(timezone.utc)
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
        """Processes agent heartbeat and updates online status."""
        stmt = select(Sensor).where(Sensor.id == sensor_id)
        res = await db.execute(stmt)
        sensor = res.scalar_one_or_none()
        if not sensor or sensor.status == "REVOKED":
            raise AuthenticationError(detail="Sensor agent not found or revoked.")

        token_hash = cls._hash_token(raw_token)
        if sensor.enrollment_token_hash != token_hash:
            raise AuthenticationError(detail="Invalid sensor enrollment credentials.")

        sensor.status = "ONLINE"
        sensor.last_heartbeat = datetime.now(timezone.utc)
        await db.flush()
        return sensor

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
        tenant_id: str
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
        await db.flush()
        return True
