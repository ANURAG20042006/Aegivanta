"""
backend/app/services/zero_trust_engine.py
=========================================
Phase 22 Zero-Trust Device Posture & Continuous Authorization Engine.
Evaluates endpoint trust scores and computes real-time dynamic access decisions.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.endpoint_xdr import ZeroTrustDevicePosture

logger = logging.getLogger("Aegivanta.ZeroTrust")

DEFAULT_ZERO_TRUST_POSTURES = [
    {
        "sensor_id": "sensor-edr-node-01",
        "hostname": "WKS-EXEC-FINANCE-04",
        "user_email": "jsmith@aegivanta.enterprise",
        "os_patch_status": "CRITICAL_PATCH_MISSING",
        "edr_agent_health": "HEALTHY",
        "disk_encryption_status": "ENCRYPTED_BITLOCKER",
        "firewall_status": "ENABLED"
    },
    {
        "sensor_id": "sensor-edr-node-02",
        "hostname": "SRV-CORE-DC-01",
        "user_email": "admin@aegivanta.enterprise",
        "os_patch_status": "UP_TO_DATE",
        "edr_agent_health": "HEALTHY",
        "disk_encryption_status": "ENCRYPTED_BITLOCKER",
        "firewall_status": "ENABLED"
    },
    {
        "sensor_id": "sensor-edr-node-03",
        "hostname": "DEV-LAPTOP-MAC-12",
        "user_email": "developer@aegivanta.enterprise",
        "os_patch_status": "OUTDATED",
        "edr_agent_health": "HEALTHY",
        "disk_encryption_status": "ENCRYPTED_FILEVAULT",
        "firewall_status": "ENABLED"
    }
]


class ZeroTrustEngine:
    """Calculates endpoint device trust scores and enforces continuous authorization."""

    @classmethod
    def calculate_device_trust_score(
        cls,
        os_patch_status: str,
        edr_agent_health: str,
        disk_encryption_status: str,
        firewall_status: str
    ) -> float:
        """Calculates normalized device trust score between 0.0 and 100.0."""
        score = 100.0

        if os_patch_status == "CRITICAL_PATCH_MISSING":
            score -= 40.0
        elif os_patch_status == "OUTDATED":
            score -= 20.0

        if edr_agent_health == "MISSING":
            score -= 50.0
        elif edr_agent_health == "DEGRADED":
            score -= 25.0

        if disk_encryption_status == "UNENCRYPTED":
            score -= 25.0

        if firewall_status == "DISABLED":
            score -= 15.0

        return max(0.0, min(100.0, score))

    @classmethod
    def determine_access_decision(cls, trust_score: float) -> str:
        """Computes dynamic access decision based on calculated trust score."""
        if trust_score >= 80.0:
            return "ALLOW"
        elif trust_score >= 60.0:
            return "STEP_UP_MFA"
        elif trust_score >= 40.0:
            return "RESTRICT_ACCESS"
        else:
            return "QUARANTINE_DEVICE"

    @classmethod
    async def evaluate_and_record_posture(
        cls,
        db: AsyncSession,
        tenant_id: str,
        sensor_id: str,
        hostname: str,
        user_email: str,
        os_patch_status: str = "UP_TO_DATE",
        edr_agent_health: str = "HEALTHY",
        disk_encryption_status: str = "ENCRYPTED_BITLOCKER",
        firewall_status: str = "ENABLED"
    ) -> Dict[str, Any]:
        """Evaluates and persists zero trust device posture."""
        score = cls.calculate_device_trust_score(
            os_patch_status, edr_agent_health, disk_encryption_status, firewall_status
        )
        decision = cls.determine_access_decision(score)
        is_comp = score >= 75.0

        posture = ZeroTrustDevicePosture(
            tenant_id=tenant_id,
            sensor_id=sensor_id,
            hostname=hostname,
            user_email=user_email,
            device_trust_score=score,
            is_compliant=is_comp,
            os_patch_status=os_patch_status,
            edr_agent_health=edr_agent_health,
            disk_encryption_status=disk_encryption_status,
            firewall_status=firewall_status,
            access_decision=decision,
            evaluated_at=datetime.now(timezone.utc)
        )
        db.add(posture)
        await db.flush()

        return {
            "id": posture.id,
            "sensor_id": posture.sensor_id,
            "hostname": posture.hostname,
            "user_email": posture.user_email,
            "device_trust_score": posture.device_trust_score,
            "is_compliant": posture.is_compliant,
            "access_decision": posture.access_decision,
            "evaluated_at": posture.evaluated_at.isoformat()
        }

    @classmethod
    async def list_device_postures(
        cls,
        db: AsyncSession,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Lists device postures across tenant fleet."""
        stmt = select(ZeroTrustDevicePosture).where(
            ZeroTrustDevicePosture.tenant_id == tenant_id
        ).order_by(desc(ZeroTrustDevicePosture.evaluated_at))

        postures = list((await db.execute(stmt)).scalars().all())
        if not postures:
            # Seed default postures
            for p in DEFAULT_ZERO_TRUST_POSTURES:
                await cls.evaluate_and_record_posture(
                    db=db,
                    tenant_id=tenant_id,
                    sensor_id=p["sensor_id"],
                    hostname=p["hostname"],
                    user_email=p["user_email"],
                    os_patch_status=p["os_patch_status"],
                    edr_agent_health=p["edr_agent_health"],
                    disk_encryption_status=p["disk_encryption_status"],
                    firewall_status=p["firewall_status"]
                )
            stmt2 = select(ZeroTrustDevicePosture).where(
                ZeroTrustDevicePosture.tenant_id == tenant_id
            ).order_by(desc(ZeroTrustDevicePosture.evaluated_at))
            postures = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": p.id,
                "sensor_id": p.sensor_id,
                "hostname": p.hostname,
                "user_email": p.user_email,
                "device_trust_score": p.device_trust_score,
                "is_compliant": p.is_compliant,
                "os_patch_status": p.os_patch_status,
                "edr_agent_health": p.edr_agent_health,
                "disk_encryption_status": p.disk_encryption_status,
                "firewall_status": p.firewall_status,
                "access_decision": p.access_decision,
                "evaluated_at": p.evaluated_at.isoformat() if p.evaluated_at else None
            }
            for p in postures
        ]
