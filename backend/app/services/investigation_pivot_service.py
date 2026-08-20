"""
backend/app/services/investigation_pivot_service.py
==================================================
Phase 3.8 Multi-Dimensional Entity Pivoting Service.
Enables analysts to pivot across IPs, Users, Assets, IOCs, and Incidents.
"""

from typing import Dict, Any, List, Optional
import logging
from sqlalchemy import select, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.incident import Incident
from backend.app.models.alert import Alert
from backend.app.models.security_event import SecurityEvent
from backend.app.models.threat_intel import ThreatIndicator
from backend.app.models.response import ResponseActionRecord

logger = logging.getLogger("SentinelAI")


class InvestigationPivotService:
    """Provides high-performance multi-hop entity pivot expansions."""

    @classmethod
    async def pivot_entity(
        cls,
        entity_type: str,
        entity_value: str,
        limit: int = 50,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Pivots on an entity seed (IP, USER, ASSET, IOC, INCIDENT) and returns correlated SOC objects.
        """
        etype = entity_type.upper().strip()
        evalue = entity_value.strip()

        pivots: Dict[str, Any] = {
            "seed_entity_type": etype,
            "seed_entity_value": evalue,
            "related_incidents": [],
            "related_alerts": [],
            "related_events": [],
            "related_iocs": [],
            "related_actions": []
        }

        if not db:
            return pivots

        if etype in ["IP", "HOST"]:
            # Query Incidents
            res_inc = await db.execute(
                select(Incident).where(
                    or_(Incident.source_ip == evalue, Incident.destination_ip == evalue)
                ).limit(limit)
            )
            pivots["related_incidents"] = [
                {"id": i.id, "code": i.incident_code, "severity": i.severity, "risk_score": i.risk_score, "attack_type": i.attack_type}
                for i in res_inc.scalars().all()
            ]

            # Query Alerts
            res_alt = await db.execute(
                select(Alert).where(
                    or_(Alert.source_ip == evalue, Alert.destination_ip == evalue)
                ).limit(limit)
            )
            pivots["related_alerts"] = [
                {"id": a.id, "title": a.title, "severity": a.severity, "attack_type": a.attack_type}
                for a in res_alt.scalars().all()
            ]

            # Query IOCs
            res_ioc = await db.execute(
                select(ThreatIndicator).where(ThreatIndicator.normalized_value == evalue)
            )
            pivots["related_iocs"] = [
                {"id": i.id, "type": i.ioc_type, "severity": i.severity, "source": i.source}
                for i in res_ioc.scalars().all()
            ]

            # Query Response Actions
            res_act = await db.execute(
                select(ResponseActionRecord).where(ResponseActionRecord.target_entity == evalue).limit(limit)
            )
            pivots["related_actions"] = [
                {"id": act.id, "action_type": act.action_type, "status": act.status, "is_dry_run": act.is_dry_run}
                for act in res_act.scalars().all()
            ]

        elif etype == "IOC":
            res_ioc = await db.execute(
                select(ThreatIndicator).where(ThreatIndicator.normalized_value == evalue)
            )
            pivots["related_iocs"] = [
                {"id": i.id, "type": i.ioc_type, "severity": i.severity, "source": i.source}
                for i in res_ioc.scalars().all()
            ]

            # Query Incidents where IOC matches source/dest IP
            res_inc = await db.execute(
                select(Incident).where(
                    or_(Incident.source_ip == evalue, Incident.destination_ip == evalue)
                ).limit(limit)
            )
            pivots["related_incidents"] = [
                {"id": i.id, "code": i.incident_code, "severity": i.severity, "risk_score": i.risk_score}
                for i in res_inc.scalars().all()
            ]

        return pivots
