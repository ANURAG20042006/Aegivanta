"""
backend/app/services/autonomous_mission_service.py
===================================================
Phase 49 — Autonomous Cyber Defense Mission management service.
Orchestrates high-level autonomous defense mission directives, blast radius constraints,
and tactical containment objectives.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.autonomous_control_plane import AutonomousDefenseMission


_MISSION_SEEDS = [
    {
        "mission_code": "MISSION-AEGIS-01",
        "mission_name": "Operation Aegis Overwatch",
        "objective": "Continuous real-time threat neutralization across cloud workloads, edge points of presence, and microsegmentation connectors.",
        "threat_tier": "CRITICAL",
        "mission_status": "ACTIVE",
        "autonomy_level": "FULL_AUTONOMY",
        "blast_radius_limit_usd": 150000.0,
        "actions_executed_count": 84,
        "threats_neutralized_count": 31,
        "success_rate": 0.991,
        "kill_switch_engaged": False,
    },
    {
        "mission_code": "MISSION-LOCKDOWN-02",
        "mission_name": "Operation Sovereign Perimeter",
        "objective": "Zero-trust network lockdown enforcing cryptographic host attestation and MFA session step-up upon threat anomaly detection.",
        "threat_tier": "HIGH",
        "mission_status": "ACTIVE",
        "autonomy_level": "SEMI_AUTONOMOUS",
        "blast_radius_limit_usd": 50000.0,
        "actions_executed_count": 52,
        "threats_neutralized_count": 18,
        "success_rate": 0.985,
        "kill_switch_engaged": False,
    },
    {
        "mission_code": "MISSION-RANSOM-03",
        "mission_name": "Operation Ransomware Rapid Eradication",
        "objective": "Immediate shadow copy recovery, file-system process killing, and dynamic honeypot diversion upon suspicious canary file alteration.",
        "threat_tier": "NATION_STATE",
        "mission_status": "COMPLETED",
        "autonomy_level": "FULL_AUTONOMY",
        "blast_radius_limit_usd": 500000.0,
        "actions_executed_count": 128,
        "threats_neutralized_count": 56,
        "success_rate": 0.994,
        "kill_switch_engaged": False,
    },
]


class AutonomousMissionService:

    @classmethod
    async def list_missions(
        cls,
        db: AsyncSession,
        tenant_id: str = "default-tenant",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists autonomous defense missions. In demo/lab mode, seeds defaults if empty."""
        from backend.app.config import settings
        is_production = (
            getattr(settings, "OPERATING_MODE", "").upper() == "PRODUCTION" or
            getattr(settings, "APP_ENV", "").lower() == "production" or
            getattr(settings, "AEGIVANTA_ENVIRONMENT", "").upper() == "PRODUCTION"
        )
        result = await db.execute(
            select(AutonomousDefenseMission)
            .where(AutonomousDefenseMission.tenant_id == tenant_id)
            .order_by(AutonomousDefenseMission.started_at.desc())
            .limit(limit)
        )
        missions = result.scalars().all()

        if not missions and not is_production:
            await cls._seed_defaults(db, tenant_id)
            result2 = await db.execute(
                select(AutonomousDefenseMission)
                .where(AutonomousDefenseMission.tenant_id == tenant_id)
                .order_by(AutonomousDefenseMission.started_at.desc())
                .limit(limit)
            )
            missions = result2.scalars().all()

        return [cls._serialize(m) for m in missions]


    @classmethod
    async def create_mission(
        cls,
        db: AsyncSession,
        tenant_id: str,
        mission_name: str,
        mission_code: str,
        objective: str,
        threat_tier: str = "CRITICAL",
        autonomy_level: str = "FULL_AUTONOMY",
        blast_radius_limit_usd: float = 100000.0,
    ) -> Dict[str, Any]:
        """Launches a new autonomous cyber defense mission."""
        mission = AutonomousDefenseMission(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            mission_name=mission_name,
            mission_code=mission_code,
            objective=objective,
            threat_tier=threat_tier,
            mission_status="ACTIVE",
            autonomy_level=autonomy_level,
            blast_radius_limit_usd=blast_radius_limit_usd,
            actions_executed_count=0,
            threats_neutralized_count=0,
            success_rate=1.0,
            kill_switch_engaged=False,
            started_at=datetime.now(timezone.utc)
        )
        db.add(mission)
        await db.flush()
        return cls._serialize(mission)

    @classmethod
    async def _seed_defaults(cls, db: AsyncSession, tenant_id: str) -> None:
        for seed in _MISSION_SEEDS:
            db.add(AutonomousDefenseMission(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                mission_code=seed["mission_code"],
                mission_name=seed["mission_name"],
                objective=seed["objective"],
                threat_tier=seed["threat_tier"],
                mission_status=seed["mission_status"],
                autonomy_level=seed["autonomy_level"],
                blast_radius_limit_usd=seed["blast_radius_limit_usd"],
                actions_executed_count=seed["actions_executed_count"],
                threats_neutralized_count=seed["threats_neutralized_count"],
                success_rate=seed["success_rate"],
                kill_switch_engaged=seed["kill_switch_engaged"],
                started_at=datetime.now(timezone.utc)
            ))
        await db.flush()

    @staticmethod
    def _serialize(m: AutonomousDefenseMission) -> Dict[str, Any]:
        return {
            "id": m.id,
            "mission_code": m.mission_code,
            "mission_name": m.mission_name,
            "objective": m.objective,
            "threat_tier": m.threat_tier,
            "mission_status": m.mission_status,
            "autonomy_level": m.autonomy_level,
            "blast_radius_limit_usd": m.blast_radius_limit_usd,
            "actions_executed_count": m.actions_executed_count,
            "threats_neutralized_count": m.threats_neutralized_count,
            "success_rate": m.success_rate,
            "kill_switch_engaged": m.kill_switch_engaged,
            "started_at": m.started_at.isoformat() if m.started_at else None,
            "completed_at": m.completed_at.isoformat() if m.completed_at else None
        }
