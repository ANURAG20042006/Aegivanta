"""
backend/app/services/investigation_case_service.py
==================================================
Phase 3.8 Investigation Case Management Service.
Handles complete lifecycle, evidence aggregation, timeline events, and notes for SOC investigations.
"""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.investigation import (
    InvestigationCase, InvestigationNote, InvestigationEvidence, InvestigationTimeline,
    is_valid_case_transition, VALID_CASE_STATUSES
)
from backend.app.models.incident import Incident

logger = logging.getLogger("SentinelAI")


class InvestigationCaseService:
    """Primary service for creating, managing, and resolving SOC investigation cases."""

    @classmethod
    async def create_case(
        cls,
        title: str,
        description: Optional[str] = None,
        priority: str = "HIGH",
        severity: str = "HIGH",
        analyst: str = "unassigned",
        linked_incident_ids: Optional[List[str]] = None,
        linked_assets: Optional[List[str]] = None,
        linked_users: Optional[List[str]] = None,
        linked_iocs: Optional[List[str]] = None,
        mitre_techniques: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        risk_score: float = 50.0,
        db: Optional[AsyncSession] = None
    ) -> InvestigationCase:
        """Creates a new structured investigation case."""
        case_id = str(uuid.uuid4())
        short_code = f"CASE-{case_id[:8].upper()}"

        case = InvestigationCase(
            id=case_id,
            case_code=short_code,
            title=title,
            description=description,
            priority=priority.upper(),
            severity=severity.upper(),
            status="OPEN",
            analyst=analyst,
            linked_incident_ids=linked_incident_ids or [],
            linked_assets=linked_assets or [],
            linked_users=linked_users or [],
            linked_iocs=linked_iocs or [],
            mitre_techniques=mitre_techniques or [],
            tags=tags or [],
            risk_score=risk_score
        )

        if db:
            db.add(case)

            # Initial Timeline event
            tl = InvestigationTimeline(
                id=str(uuid.uuid4()),
                case_id=case_id,
                event_type="CASE_CREATED",
                title="Investigation Case Opened",
                description=f"Investigation '{title}' initialized by {analyst}.",
                actor=analyst,
                metadata_json={"priority": priority, "severity": severity}
            )
            db.add(tl)
            await db.commit()
            await db.refresh(case)

        logger.info("Created investigation case %s (%s)", short_code, title)
        return case

    @classmethod
    async def get_case(cls, case_id: str, db: AsyncSession) -> Optional[InvestigationCase]:
        query = (
            select(InvestigationCase)
            .where(or_case_match(case_id))
            .options(
                selectinload(InvestigationCase.notes),
                selectinload(InvestigationCase.evidence_items),
                selectinload(InvestigationCase.timeline_events)
            )
        )
        res = await db.execute(query)
        return res.scalar_one_or_none()

    @classmethod
    async def list_cases(
        cls,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
        analyst_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        db: Optional[AsyncSession] = None
    ) -> List[InvestigationCase]:
        if not db:
            return []

        query = select(InvestigationCase)
        if status_filter:
            query = query.where(InvestigationCase.status == status_filter.upper())
        if priority_filter:
            query = query.where(InvestigationCase.priority == priority_filter.upper())
        if severity_filter:
            query = query.where(InvestigationCase.severity == severity_filter.upper())
        if analyst_filter:
            query = query.where(InvestigationCase.analyst == analyst_filter)

        query = query.order_by(desc(InvestigationCase.created_at)).offset(offset).limit(limit)
        res = await db.execute(query)
        return res.scalars().all()

    @classmethod
    async def update_case(
        cls,
        case_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        analyst: Optional[str] = None,
        tags: Optional[List[str]] = None,
        actor: str = "analyst",
        db: Optional[AsyncSession] = None
    ) -> InvestigationCase:
        case = await cls.get_case(case_id, db)
        if not case:
            raise LookupError(f"Investigation case '{case_id}' not found.")

        if status:
            new_status = status.upper().strip()
            if new_status not in VALID_CASE_STATUSES:
                raise ValueError(f"Invalid status: '{new_status}'. Allowed: {VALID_CASE_STATUSES}")
            if not is_valid_case_transition(case.status, new_status):
                raise ValueError(f"Invalid transition from '{case.status}' to '{new_status}'.")
            case.status = new_status

        if title:
            case.title = title
        if description is not None:
            case.description = description
        if priority:
            case.priority = priority.upper()
        if severity:
            case.severity = severity.upper()
        if analyst:
            case.analyst = analyst
        if tags is not None:
            case.tags = tags

        case.updated_at = datetime.now(timezone.utc)

        if db:
            tl = InvestigationTimeline(
                id=str(uuid.uuid4()),
                case_id=case.id,
                event_type="CASE_UPDATED",
                title=f"Case Updated (Status: {case.status})",
                description=f"Investigation modified by {actor}.",
                actor=actor,
                metadata_json={"status": case.status, "priority": case.priority}
            )
            db.add(tl)
            await db.commit()
            await db.refresh(case)

        return case

    @classmethod
    async def add_evidence(
        cls,
        case_id: str,
        evidence_type: str,
        reference_id: Optional[str],
        description: str,
        metadata_json: Optional[Dict[str, Any]] = None,
        actor: str = "analyst",
        db: Optional[AsyncSession] = None
    ) -> InvestigationEvidence:
        case = await cls.get_case(case_id, db)
        if not case:
            raise LookupError(f"Investigation case '{case_id}' not found.")

        ev_id = str(uuid.uuid4())
        ev = InvestigationEvidence(
            id=ev_id,
            case_id=case.id,
            evidence_type=evidence_type.upper(),
            reference_id=reference_id,
            description=description,
            metadata_json=metadata_json or {},
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None)
        )

        if db:
            db.add(ev)
            tl = InvestigationTimeline(
                id=str(uuid.uuid4()),
                case_id=case.id,
                event_type="EVIDENCE_ADDED",
                title=f"Evidence Added: {evidence_type}",
                description=description,
                actor=actor,
                metadata_json={"evidence_id": ev_id, "evidence_type": evidence_type}
            )
            db.add(tl)
            await db.commit()
            await db.refresh(ev)

        return ev

    @classmethod
    async def add_note(
        cls,
        case_id: str,
        author: str,
        content: str,
        db: AsyncSession
    ) -> InvestigationNote:
        case = await cls.get_case(case_id, db)
        if not case:
            raise LookupError(f"Investigation case '{case_id}' not found.")

        note_id = str(uuid.uuid4())
        note = InvestigationNote(
            id=note_id,
            case_id=case.id,
            author=author,
            content=content
        )
        db.add(note)

        tl = InvestigationTimeline(
            id=str(uuid.uuid4()),
            case_id=case.id,
            event_type="NOTE_ADDED",
            title="Analyst Note Recorded",
            description=content[:200],
            actor=author,
            metadata_json={"note_id": note_id}
        )
        db.add(tl)
        await db.commit()
        await db.refresh(note)
        return note

    @classmethod
    async def close_case(
        cls,
        case_id: str,
        closed_by: str,
        resolution_summary: str,
        db: AsyncSession
    ) -> InvestigationCase:
        case = await cls.get_case(case_id, db)
        if not case:
            raise LookupError(f"Investigation case '{case_id}' not found.")

        case.status = "CLOSED"
        case.closed_at = datetime.now(timezone.utc)
        case.updated_at = datetime.now(timezone.utc)

        tl = InvestigationTimeline(
            id=str(uuid.uuid4()),
            case_id=case.id,
            event_type="CASE_CLOSED",
            title="Investigation Closed",
            description=f"Case formally resolved by {closed_by}. Summary: {resolution_summary}",
            actor=closed_by,
            metadata_json={"resolution": resolution_summary}
        )
        db.add(tl)
        await db.commit()
        await db.refresh(case)
        return case

    @classmethod
    async def get_statistics(cls, db: AsyncSession) -> Dict[str, Any]:
        res_status = await db.execute(
            select(InvestigationCase.status, func.count(InvestigationCase.id)).group_by(InvestigationCase.status)
        )
        status_counts = dict(res_status.all())

        res_priority = await db.execute(
            select(InvestigationCase.priority, func.count(InvestigationCase.id)).group_by(InvestigationCase.priority)
        )
        priority_counts = dict(res_priority.all())

        total = sum(status_counts.values())
        active = sum(v for k, v in status_counts.items() if k != "CLOSED")

        return {
            "total_cases": total,
            "active_cases": active,
            "by_status": status_counts,
            "by_priority": priority_counts,
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }


def or_case_match(case_id: str):
    from sqlalchemy import or_
    return or_(InvestigationCase.id == case_id, InvestigationCase.case_code == case_id)
