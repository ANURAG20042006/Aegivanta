"""
backend/app/services/response_orchestrator.py
=============================================
Controlled SOAR Response Orchestrator & Multi-Tier Approval Workflow Engine.
Enforces strict least privilege, audit logging, simulation-first defaults, and authorization gates.
"""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.response_approval import ResponseApproval
from backend.app.models.incident import Incident
from backend.app.models.incident_timeline import IncidentTimelineEvent
from backend.app.services.playbook_service import PlaybookService

logger = logging.getLogger("SentinelAI")


class ResponseOrchestrator:
    """Core SOAR Approval & Execution Orchestrator."""

    SUPPORTED_ACTIONS = {
        "NOTIFY_ANALYST": {"severity": "LOW", "is_destructive": False},
        "CREATE_TICKET": {"severity": "LOW", "is_destructive": False},
        "ESCALATE_INCIDENT": {"severity": "MEDIUM", "is_destructive": False},
        "BLOCK_IOC_SIMULATION": {"severity": "HIGH", "is_destructive": True},
        "ISOLATE_ASSET_SIMULATION": {"severity": "HIGH", "is_destructive": True},
        "DISABLE_ACCOUNT_SIMULATION": {"severity": "HIGH", "is_destructive": True},
    }

    @staticmethod
    async def request_action(
        incident_id: str,
        requested_action: str,
        target_entity: str,
        requested_by: str,
        parameters: Optional[Dict[str, Any]],
        db: AsyncSession
    ) -> ResponseApproval:
        """Submits an action for two-tier approval."""
        if requested_action not in ResponseOrchestrator.SUPPORTED_ACTIONS:
            raise ValueError(f"Unsupported response action: {requested_action}")

        # Check Incident Exists
        res = await db.execute(select(Incident).where(Incident.id == incident_id))
        inc = res.scalar_one_or_none()
        if not inc:
            raise ValueError(f"Incident {incident_id} not found")

        req = ResponseApproval(
            id=str(uuid.uuid4()),
            incident_id=incident_id,
            requested_action=requested_action,
            target_entity=target_entity,
            parameters=parameters or {},
            requested_by=requested_by,
            requested_at=datetime.now(timezone.utc),
            status="REQUESTED",
            is_dry_run=True  # Strict simulation default
        )
        db.add(req)
        await db.commit()
        await db.refresh(req)

        logger.info(f"Response action {requested_action} on {target_entity} requested by {requested_by} (ID: {req.id})")
        return req

    @staticmethod
    async def approve_and_execute(
        approval_id: str,
        approved_by: str,
        approver_role: str,
        force_live: bool = False,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """Approves and executes a requested SOAR response action."""
        if approver_role != "admin":
            raise PermissionError("Only Admin users are authorized to approve and execute response actions.")

        res = await db.execute(select(ResponseApproval).where(ResponseApproval.id == approval_id))
        req = res.scalar_one_or_none()
        if not req:
            raise ValueError(f"Approval request {approval_id} not found")
        if req.status != "REQUESTED":
            raise ValueError(f"Approval request is already {req.status}")

        now_utc = datetime.now(timezone.utc)
        req.approved_by = approved_by
        req.approved_at = now_utc
        req.status = "EXECUTING"
        await db.flush()

        # Execute via PlaybookService (simulation dry-run by default)
        is_dry_run = not force_live
        exec_res = await PlaybookService.execute_action(
            incident_id=req.incident_id,
            playbook_name=f"SOAR_{req.requested_action}",
            action_type=req.requested_action,
            target_entity=req.target_entity,
            is_dry_run=is_dry_run,
            executed_by=approved_by,
            parameters=req.parameters or {},
            db=db
        )

        req.status = "COMPLETED" if exec_res.get("status") in ["SIMULATED_SUCCESS", "SUCCESS"] else "FAILED"
        req.execution_id = exec_res.get("execution_id")
        req.execution_result = exec_res
        req.audit_id = exec_res.get("audit_id")
        await db.commit()

        return {
            "approval_id": req.id,
            "status": req.status,
            "execution": exec_res
        }

    @staticmethod
    async def reject_action(
        approval_id: str,
        rejected_by: str,
        approver_role: str,
        reason: str,
        db: AsyncSession
    ) -> ResponseApproval:
        """Rejects a pending response action request."""
        if approver_role not in ["admin", "analyst"]:
            raise PermissionError("Viewer role cannot reject response requests.")

        res = await db.execute(select(ResponseApproval).where(ResponseApproval.id == approval_id))
        req = res.scalar_one_or_none()
        if not req:
            raise ValueError(f"Approval request {approval_id} not found")
        if req.status != "REQUESTED":
            raise ValueError(f"Approval request is already {req.status}")

        req.rejected_by = rejected_by
        req.rejected_at = datetime.now(timezone.utc)
        req.status = "REJECTED"
        req.reason = reason
        await db.commit()
        await db.refresh(req)
        return req

    @staticmethod
    async def list_requests(
        status_filter: Optional[str] = None,
        limit: int = 50,
        db: AsyncSession = None
    ) -> List[ResponseApproval]:
        """Lists pending or historical response approval requests."""
        stmt = select(ResponseApproval)
        if status_filter:
            stmt = stmt.where(ResponseApproval.status == status_filter.upper())
        stmt = stmt.order_by(desc(ResponseApproval.requested_at)).limit(limit)
        res = await db.execute(stmt)
        return res.scalars().all()
