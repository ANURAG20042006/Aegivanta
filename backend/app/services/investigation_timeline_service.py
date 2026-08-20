"""
backend/app/services/investigation_timeline_service.py
======================================================
Phase 3.6 Automated Investigation Timeline Service.
Constructs chronological investigation timelines and attack progression summaries for incidents.
"""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.incident import Incident
from backend.app.models.incident_timeline import IncidentTimelineEvent

logger = logging.getLogger("SentinelAI")


class InvestigationTimelineService:
    """
    Automates chronological timeline reconstruction and forensic summaries for security incidents.
    """

    @staticmethod
    async def get_incident_timeline(incident_id: str, db: AsyncSession) -> Dict[str, Any]:
        """
        Retrieves full chronological investigation timeline and structured progression summary.
        """
        query_inc = select(Incident).where(
            (Incident.id == incident_id) | (Incident.incident_code == incident_id)
        )
        res_inc = await db.execute(query_inc)
        inc = res_inc.scalar_one_or_none()
        if not inc:
            raise LookupError(f"Incident '{incident_id}' not found.")

        # Fetch timeline events
        query_tl = select(IncidentTimelineEvent).where(
            IncidentTimelineEvent.incident_id == inc.id
        ).order_by(IncidentTimelineEvent.timestamp.asc())
        res_tl = await db.execute(query_tl)
        events = res_tl.scalars().all()

        formatted_events = []
        for ev in events:
            formatted_events.append({
                "id": ev.id,
                "timestamp": ev.timestamp.isoformat(),
                "event_type": ev.event_type,
                "title": ev.title,
                "description": ev.description,
                "actor": ev.actor,
                "metadata": ev.metadata_payload or {}
            })

        # Generate attack progression summary
        first_seen = inc.first_seen or inc.timestamp
        last_seen = inc.last_seen or inc.timestamp
        duration_mins = max((last_seen - first_seen).total_seconds() / 60.0, 1.0)

        summary = {
            "incident_id": inc.id,
            "incident_code": inc.incident_code,
            "status": inc.status,
            "severity": inc.severity,
            "risk_score": inc.risk_score,
            "total_timeline_entries": len(formatted_events),
            "attack_type": inc.attack_type,
            "source_ip": inc.source_ip,
            "destination_ip": inc.destination_ip,
            "first_seen": first_seen.isoformat(),
            "last_seen": last_seen.isoformat(),
            "incident_duration_minutes": round(duration_mins, 2),
            "assigned_analyst": inc.analyst or "Unassigned",
            "is_resolved": inc.status in ["RESOLVED", "CLOSED"]
        }

        return {
            "summary": summary,
            "timeline": formatted_events
        }

    @staticmethod
    async def record_timeline_entry(
        incident_id: str,
        event_type: str,
        title: str,
        description: Optional[str] = None,
        actor: str = "SYSTEM",
        metadata: Optional[Dict[str, Any]] = None,
        db: AsyncSession = None
    ) -> IncidentTimelineEvent:
        """Appends a new chronological entry to the incident investigation timeline."""
        ev = IncidentTimelineEvent(
            incident_id=incident_id,
            event_type=event_type,
            title=title,
            description=description,
            actor=actor,
            metadata_payload=metadata or {}
        )
        db.add(ev)
        await db.commit()
        await db.refresh(ev)
        return ev
