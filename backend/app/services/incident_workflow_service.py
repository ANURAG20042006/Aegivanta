"""
backend/app/services/incident_workflow_service.py
=================================================
Phase 16.4 & 16.5 Incident Workflow, State Machine, and Immutable Timeline Engine.
Enforces multi-stage SOC triage state transitions, analyst ownership assignment,
audited notes, resolution tracking, and chronological timeline event generation.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.incident import Incident
from backend.app.models.incident_timeline import IncidentTimelineEvent
from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType
from backend.app.core.exceptions import SentinelAIException

logger = logging.getLogger("Aegivanta.IncidentWorkflow")

PHASE16_VALID_STATUSES = [
    "NEW",
    "TRIAGED",
    "INVESTIGATING",
    "CONTAINMENT_PENDING",
    "CONTAINED",
    "REMEDIATING",
    "RESOLVED",
    "FALSE_POSITIVE",
    "CLOSED"
]

PHASE16_ALLOWED_TRANSITIONS = {
    "NEW": ["TRIAGED", "INVESTIGATING", "FALSE_POSITIVE"],
    "DETECTED": ["TRIAGED", "INVESTIGATING", "FALSE_POSITIVE"],
    "OPEN": ["TRIAGED", "INVESTIGATING", "FALSE_POSITIVE"],
    "TRIAGED": ["INVESTIGATING", "CONTAINMENT_PENDING", "CONTAINED", "FALSE_POSITIVE", "CLOSED"],
    "INVESTIGATING": ["CONTAINMENT_PENDING", "CONTAINED", "REMEDIATING", "RESOLVED", "FALSE_POSITIVE"],
    "CONTAINMENT_PENDING": ["CONTAINED", "INVESTIGATING"],
    "CONTAINED": ["REMEDIATING", "RESOLVED"],
    "REMEDIATING": ["RESOLVED", "INVESTIGATING"],
    "RESOLVED": ["CLOSED", "INVESTIGATING"],
    "FALSE_POSITIVE": ["CLOSED"],
    "CLOSED": ["INVESTIGATING"] # Reopen if needed
}


class IncidentWorkflowService:
    """Manages incident lifecycle transitions, analyst triage notes, and immutable timeline logging."""

    @classmethod
    async def append_timeline_event(
        cls,
        db: AsyncSession,
        incident_id: str,
        event_type: str,
        title: str,
        description: str,
        actor: str = "SYSTEM",
        metadata: Optional[Dict[str, Any]] = None
    ) -> IncidentTimelineEvent:
        """Appends an immutable chronological event to the incident timeline."""
        event = IncidentTimelineEvent(
            incident_id=incident_id,
            event_type=event_type,
            title=title,
            description=description,
            actor=actor,
            metadata_payload=metadata or {},
            timestamp=datetime.now(timezone.utc)
        )
        db.add(event)
        await db.flush()
        return event

    @classmethod
    async def get_incident_timeline(
        cls,
        db: AsyncSession,
        incident_id: str
    ) -> List[Dict[str, Any]]:
        """Retrieves chronologically sorted immutable timeline events for an incident."""
        stmt = (
            select(IncidentTimelineEvent)
            .where(IncidentTimelineEvent.incident_id == incident_id)
            .order_by(IncidentTimelineEvent.timestamp.asc())
        )
        res = await db.execute(stmt)
        events = list(res.scalars().all())

        return [
            {
                "id": ev.id,
                "incident_id": ev.incident_id,
                "timestamp": ev.timestamp.isoformat(),
                "event_type": ev.event_type,
                "title": ev.title,
                "description": ev.description,
                "actor": ev.actor,
                "metadata": ev.metadata_payload
            }
            for ev in events
        ]

    @classmethod
    async def transition_incident_status(
        cls,
        db: AsyncSession,
        incident_id: str,
        new_status: str,
        actor: str,
        reason: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Incident:
        """Validates and executes an audited incident lifecycle status transition."""
        status_norm = new_status.upper().strip()
        if status_norm not in PHASE16_VALID_STATUSES:
            raise SentinelAIException(status_code=400, detail=f"Invalid status '{new_status}'. Allowed: {PHASE16_VALID_STATUSES}")

        stmt = select(Incident).where(Incident.id == incident_id)
        res = await db.execute(stmt)
        incident = res.scalar_one_or_none()
        if not incident:
            raise SentinelAIException(status_code=404, detail="Incident not found.")

        current = incident.status.upper()
        allowed = PHASE16_ALLOWED_TRANSITIONS.get(current, [])
        if status_norm != current and status_norm not in allowed:
            raise SentinelAIException(
                status_code=400,
                detail=f"Invalid state transition from '{current}' to '{status_norm}'. Allowed: {allowed}"
            )

        now = datetime.now(timezone.utc)
        incident.status = status_norm

        if status_norm == "TRIAGED" and not incident.triaged_at:
            incident.triaged_at = now
        elif status_norm in ["RESOLVED", "CLOSED"]:
            incident.closed_at = now
            if reason:
                incident.resolution = reason

        if notes:
            existing = incident.notes or ""
            timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
            incident.notes = f"{existing}\n[{timestamp_str} by {actor}]: {notes}".strip()

        # Append to Timeline
        await cls.append_timeline_event(
            db=db,
            incident_id=incident.id,
            event_type="STATUS_CHANGE",
            title=f"Status changed from {current} to {status_norm}",
            description=f"Action by {actor}. Reason: {reason or 'Standard workflow transition'}",
            actor=actor,
            metadata={"previous_status": current, "new_status": status_norm, "reason": reason}
        )

        await db.flush()
        return incident

    @classmethod
    async def assign_incident_analyst(
        cls,
        db: AsyncSession,
        incident_id: str,
        analyst_username: str,
        actor: str
    ) -> Incident:
        """Assigns primary investigation ownership to an analyst."""
        stmt = select(Incident).where(Incident.id == incident_id)
        res = await db.execute(stmt)
        incident = res.scalar_one_or_none()
        if not incident:
            raise SentinelAIException(status_code=404, detail="Incident not found.")

        prev_analyst = incident.analyst or "Unassigned"
        incident.analyst = analyst_username

        await cls.append_timeline_event(
            db=db,
            incident_id=incident.id,
            event_type="ANALYST_ASSIGNMENT",
            title=f"Ownership reassigned to {analyst_username}",
            description=f"Previously assigned to: {prev_analyst}",
            actor=actor,
            metadata={"previous_analyst": prev_analyst, "new_analyst": analyst_username}
        )

        await db.flush()
        return incident
