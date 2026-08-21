"""
backend/app/services/soc_case_management_service.py
===================================================
Phase 26.6 Enterprise SOC Case Management Service.
Manages full investigation case lifecycle across 9 states:
OPEN -> TRIAGED -> INVESTIGATING -> CONTAINMENT -> REMEDIATION -> MONITORING -> RESOLVED -> CLOSED -> REOPENED.
Enforces SLA tracking, tasks, analyst comments, and immutable audit logging.
"""

import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.soc_case import (
    SOCCase, SOCCaseTask, SOCCaseComment, SOCCaseAudit,
    SOC_CASE_STATUSES, SOC_CASE_PRIORITIES
)
from backend.app.core.exceptions import SentinelAIException

logger = logging.getLogger("Aegivanta.SOCCaseManagement")


class SOCCaseManagementService:
    """Enterprise SOC Case lifecycle management, collaboration, and SLA tracking service."""

    @classmethod
    async def create_case(
        cls,
        db: AsyncSession,
        tenant_id: str,
        title: str,
        description: str,
        priority: str = "HIGH",
        severity: str = "HIGH",
        lead_analyst_id: Optional[str] = None,
        linked_incident_ids: Optional[List[str]] = None,
        linked_alert_ids: Optional[List[str]] = None,
        affected_assets: Optional[List[str]] = None,
        affected_identities: Optional[List[str]] = None,
        mitre_attack_techniques: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        sla_target_hours: float = 4.0,
        risk_score: float = 75.0,
        created_by: str = "SYSTEM"
    ) -> SOCCase:
        """Creates a new SOC Case and logs an immutable audit creation event."""
        # Generate human-readable case number: CASE-YYYYMMDD-XXXX
        case_code = f"CASE-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        deadline = datetime.now(timezone.utc) + timedelta(hours=sla_target_hours)

        case = SOCCase(
            tenant_id=tenant_id,
            case_number=case_code,
            title=title,
            description=description,
            status="OPEN",
            priority=priority.upper(),
            severity=severity.upper(),
            lead_analyst_id=lead_analyst_id or "unassigned",
            assigned_team="SOC Tier 2",
            linked_incident_ids=linked_incident_ids or [],
            linked_alert_ids=linked_alert_ids or [],
            affected_assets=affected_assets or [],
            affected_identities=affected_identities or [],
            mitre_attack_techniques=mitre_attack_techniques or [],
            tags=tags or ["auto-correlated"],
            sla_target_hours=sla_target_hours,
            sla_deadline=deadline,
            is_sla_breached=False,
            risk_score=risk_score,
            containment_status="PENDING",
            created_by=created_by,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(case)
        await db.flush()

        # Audit creation event
        audit = SOCCaseAudit(
            case_id=case.id,
            tenant_id=tenant_id,
            action="CASE_CREATED",
            performed_by=created_by,
            new_state={"status": "OPEN", "priority": priority, "case_number": case_code},
            timestamp=datetime.now(timezone.utc)
        )
        db.add(audit)
        await db.flush()

        return case

    @classmethod
    async def list_cases(
        cls,
        db: AsyncSession,
        tenant_id: str,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        limit: int = 50
    ) -> List[SOCCase]:
        """Lists SOC Cases for a tenant with optional status/priority filtering."""
        query = select(SOCCase).where(SOCCase.tenant_id == tenant_id)
        if status_filter:
            query = query.where(SOCCase.status == status_filter.upper())
        if priority_filter:
            query = query.where(SOCCase.priority == priority_filter.upper())

        query = query.order_by(desc(SOCCase.created_at)).limit(limit)
        cases = list((await db.execute(query)).scalars().all())

        if not cases:
            # Seed default case for tenant
            default_case = await cls.create_case(
                db=db,
                tenant_id=tenant_id,
                title="Active Lateral Movement Investigation (WKS-EXEC-01)",
                description="Correlated anomalous PowerShell execution and multi-hop SMB probes targeting internal database servers.",
                priority="CRITICAL",
                severity="CRITICAL",
                lead_analyst_id="analyst@aegivanta.io",
                affected_assets=["WKS-EXEC-01", "SRV-DB-PROD-01"],
                affected_identities=["alice.smith"],
                mitre_attack_techniques=["T1059.001", "T1021.002"],
                risk_score=92.5
            )
            cases = [default_case]

        return cases

    @classmethod
    async def get_case_details(
        cls,
        db: AsyncSession,
        tenant_id: str,
        case_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieves comprehensive SOC Case details including tasks, comments, and audit history."""
        stmt = select(SOCCase).where(SOCCase.id == case_id, SOCCase.tenant_id == tenant_id)
        case = (await db.execute(stmt)).scalar_one_or_none()
        if not case:
            return None

        # Check SLA breach
        now = datetime.now(timezone.utc)
        if case.sla_deadline and now > case.sla_deadline and case.status not in ("RESOLVED", "CLOSED"):
            case.is_sla_breached = True

        tasks_stmt = select(SOCCaseTask).where(SOCCaseTask.case_id == case.id).order_by(SOCCaseTask.created_at)
        tasks = list((await db.execute(tasks_stmt)).scalars().all())

        comments_stmt = select(SOCCaseComment).where(SOCCaseComment.case_id == case.id).order_by(SOCCaseComment.created_at)
        comments = list((await db.execute(comments_stmt)).scalars().all())

        audits_stmt = select(SOCCaseAudit).where(SOCCaseAudit.case_id == case.id).order_by(desc(SOCCaseAudit.timestamp)).limit(20)
        audits = list((await db.execute(audits_stmt)).scalars().all())

        return {
            "id": case.id,
            "tenant_id": case.tenant_id,
            "case_number": case.case_number,
            "title": case.title,
            "description": case.description,
            "status": case.status,
            "priority": case.priority,
            "severity": case.severity,
            "lead_analyst_id": case.lead_analyst_id,
            "assigned_team": case.assigned_team,
            "linked_incident_ids": case.linked_incident_ids,
            "linked_alert_ids": case.linked_alert_ids,
            "affected_assets": case.affected_assets,
            "affected_identities": case.affected_identities,
            "mitre_attack_techniques": case.mitre_attack_techniques,
            "tags": case.tags,
            "sla_target_hours": case.sla_target_hours,
            "sla_deadline": case.sla_deadline.isoformat() if case.sla_deadline else None,
            "is_sla_breached": case.is_sla_breached,
            "risk_score": case.risk_score,
            "containment_status": case.containment_status,
            "post_incident_review": case.post_incident_review,
            "created_by": case.created_by,
            "created_at": case.created_at.isoformat(),
            "updated_at": case.updated_at.isoformat(),
            "closed_at": case.closed_at.isoformat() if case.closed_at else None,
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "assigned_to": t.assigned_to,
                    "is_completed": t.is_completed,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None
                }
                for t in tasks
            ],
            "comments": [
                {
                    "id": c.id,
                    "author": c.author,
                    "comment_text": c.comment_text,
                    "is_internal": c.is_internal,
                    "created_at": c.created_at.isoformat()
                }
                for c in comments
            ],
            "audit_trail": [
                {
                    "id": a.id,
                    "action": a.action,
                    "performed_by": a.performed_by,
                    "old_state": a.old_state,
                    "new_state": a.new_state,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in audits
            ]
        }

    @classmethod
    async def update_case_status(
        cls,
        db: AsyncSession,
        tenant_id: str,
        case_id: str,
        new_status: str,
        performed_by: str = "ANALYST"
    ) -> Dict[str, Any]:
        """Transitions case status across the 9 lifecycle states and logs an audit record."""
        stmt = select(SOCCase).where(SOCCase.id == case_id, SOCCase.tenant_id == tenant_id)
        case = (await db.execute(stmt)).scalar_one_or_none()
        if not case:
            raise SentinelAIException(status_code=404, detail="SOC Case not found.")

        norm_status = new_status.upper().strip()
        if norm_status not in SOC_CASE_STATUSES:
            raise SentinelAIException(
                status_code=400,
                detail=f"Invalid case status '{new_status}'. Allowed: {SOC_CASE_STATUSES}"
            )

        old_status = case.status
        case.status = norm_status
        case.updated_at = datetime.now(timezone.utc)
        if norm_status in ("RESOLVED", "CLOSED") and not case.closed_at:
            case.closed_at = datetime.now(timezone.utc)

        # Audit state transition
        audit = SOCCaseAudit(
            case_id=case.id,
            tenant_id=tenant_id,
            action="STATUS_CHANGED",
            performed_by=performed_by,
            old_state={"status": old_status},
            new_state={"status": norm_status},
            timestamp=datetime.now(timezone.utc)
        )
        db.add(audit)
        await db.flush()

        return {"case_id": case.id, "old_status": old_status, "new_status": norm_status}

    @classmethod
    async def add_case_comment(
        cls,
        db: AsyncSession,
        tenant_id: str,
        case_id: str,
        author: str,
        comment_text: str,
        is_internal: bool = True
    ) -> Dict[str, Any]:
        """Adds an analyst comment / investigation note to a case."""
        stmt = select(SOCCase).where(SOCCase.id == case_id, SOCCase.tenant_id == tenant_id)
        case = (await db.execute(stmt)).scalar_one_or_none()
        if not case:
            raise SentinelAIException(status_code=404, detail="SOC Case not found.")

        comment = SOCCaseComment(
            case_id=case.id,
            tenant_id=tenant_id,
            author=author,
            comment_text=comment_text,
            is_internal=is_internal,
            created_at=datetime.now(timezone.utc)
        )
        db.add(comment)

        audit = SOCCaseAudit(
            case_id=case.id,
            tenant_id=tenant_id,
            action="COMMENT_ADDED",
            performed_by=author,
            new_state={"comment_id": comment.id},
            timestamp=datetime.now(timezone.utc)
        )
        db.add(audit)
        await db.flush()

        return {"comment_id": comment.id, "author": comment.author, "created_at": comment.created_at.isoformat()}

    @classmethod
    async def add_case_task(
        cls,
        db: AsyncSession,
        tenant_id: str,
        case_id: str,
        title: str,
        description: Optional[str] = None,
        assigned_to: Optional[str] = None,
        due_date: Optional[datetime] = None,
        created_by: str = "ANALYST"
    ) -> Dict[str, Any]:
        """Adds an actionable containment / investigation task to a case."""
        stmt = select(SOCCase).where(SOCCase.id == case_id, SOCCase.tenant_id == tenant_id)
        case = (await db.execute(stmt)).scalar_one_or_none()
        if not case:
            raise SentinelAIException(status_code=404, detail="SOC Case not found.")

        task = SOCCaseTask(
            case_id=case.id,
            tenant_id=tenant_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            is_completed=False,
            due_date=due_date,
            created_at=datetime.now(timezone.utc)
        )
        db.add(task)

        audit = SOCCaseAudit(
            case_id=case.id,
            tenant_id=tenant_id,
            action="TASK_ADDED",
            performed_by=created_by,
            new_state={"task_id": task.id, "title": title},
            timestamp=datetime.now(timezone.utc)
        )
        db.add(audit)
        await db.flush()

        return {"task_id": task.id, "title": task.title, "status": "PENDING"}
