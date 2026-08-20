"""
backend/app/services/response_orchestrator.py
=============================================
Phase 3.7 Autonomous SOAR Response Orchestration Engine.
Coordinates policy evaluation, validation, multi-tier approvals, safe execution,
idempotency, cooldown enforcement, verification, rollback, and immutable audit trails.
"""

from datetime import datetime, timezone, timedelta
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.response import (
    ResponsePolicy, ResponseActionRecord, IdempotencyRecord, ResponseAuditLog,
    is_valid_action_transition, VALID_ACTION_STATUSES
)
from backend.app.models.response_approval import ResponseApproval
from backend.app.models.incident import Incident
from backend.app.models.incident_timeline import IncidentTimelineEvent
from backend.app.services.playbook_service import PlaybookService
from backend.app.services.response_policy_service import ResponsePolicyEngine
from backend.app.services.response_decision_service import ResponseDecisionService
from backend.app.services.response_actions import response_action_registry, ResponseRollbackService
from backend.app.core.dependencies import normalize_role

logger = logging.getLogger("SentinelAI")


class ResponseOrchestrator:
    """Production Autonomous Incident Response & SOAR Orchestrator."""

    SUPPORTED_ACTIONS = {
        "NOTIFY_ANALYST": {"severity": "LOW", "is_destructive": False},
        "CREATE_TICKET": {"severity": "LOW", "is_destructive": False},
        "ESCALATE_INCIDENT": {"severity": "MEDIUM", "is_destructive": False},
        "BLOCK_IOC_SIMULATION": {"severity": "HIGH", "is_destructive": True},
        "ISOLATE_ASSET_SIMULATION": {"severity": "HIGH", "is_destructive": True},
        "DISABLE_ACCOUNT_SIMULATION": {"severity": "HIGH", "is_destructive": True},
    }

    # ==========================================================================
    # LEGACY BACKWARD-COMPATIBLE WORKFLOW METHODS (PHASE 3.0-3.3)
    # ==========================================================================

    @staticmethod
    async def request_action(
        incident_id: str,
        requested_action: str,
        target_entity: str,
        requested_by: str,
        parameters: Optional[Dict[str, Any]],
        db: AsyncSession
    ) -> ResponseApproval:
        """Submits an action for legacy two-tier approval."""
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
            is_dry_run=True
        )
        db.add(req)
        await db.commit()
        await db.refresh(req)
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
        if normalize_role(approver_role) != "admin":
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

        is_dry_run = not force_live
        exec_res = await PlaybookService.execute_action(
            incident_id=req.incident_id,
            playbook_name=f"SOAR_{req.requested_action}",
            action_type=req.requested_action,
            target_entity=req.target_entity,
            is_dry_run=is_dry_run,
            executed_by=approved_by,
            parameters=req.parameters,
            db=db
        )

        req.status = "COMPLETED"
        req.execution_id = exec_res.get("execution_id")
        req.execution_result = exec_res
        req.audit_id = exec_res.get("audit_id")
        await db.commit()
        await db.refresh(req)

        return {
            "status": "COMPLETED",
            "approval_id": req.id,
            "incident_id": req.incident_id,
            "action": req.requested_action,
            "is_dry_run": is_dry_run,
            "execution_id": req.execution_id,
            "execution": exec_res,
            "execution_log": exec_res.get("execution_log")
        }

    @staticmethod
    async def reject_request(
        approval_id: str,
        rejected_by: str,
        approver_role: str,
        reason: str,
        db: AsyncSession
    ) -> ResponseApproval:
        """Rejects a pending response action request."""
        if normalize_role(approver_role) != "admin":
            raise PermissionError("Only Admin users are authorized to reject response action requests.")

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
        """Lists response approval requests with optional status filtering."""
        query = select(ResponseApproval)
        if status_filter:
            query = query.where(ResponseApproval.status == status_filter.upper())
        query = query.order_by(desc(ResponseApproval.requested_at)).limit(limit)
        res = await db.execute(query)
        return res.scalars().all()

    @classmethod
    async def preview_action(
        cls,
        incident_id: str,
        action_type: str,
        target_entity: str,
        parameters: Optional[Dict[str, Any]] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """Generates dry-run simulation preview without applying real infrastructure changes."""
        handler = response_action_registry.get_action(action_type)
        if not handler:
            raise ValueError(f"Unsupported response action type: '{action_type}'")

        # Fetch incident context if exists
        risk_score = 50.0
        severity = "HIGH"
        if db:
            res_inc = await db.execute(select(Incident).where(Incident.id == incident_id))
            inc = res_inc.scalar_one_or_none()
            if inc:
                risk_score = inc.risk_score
                severity = inc.severity

        policy_eval = await ResponsePolicyEngine.evaluate(
            risk_score=risk_score,
            severity=severity,
            requested_action=action_type,
            db=db
        )

        preview_res = handler.preview(target=target_entity, parameters=parameters)
        preview_res.update({
            "incident_id": incident_id,
            "risk_score": risk_score,
            "severity": severity,
            "policy_allowed": policy_eval["is_allowed"],
            "requires_approval": policy_eval["requires_approval"],
            "matched_policy": policy_eval.get("matched_policy_name")
        })
        return preview_res

    @classmethod
    async def submit_action(
        cls,
        incident_id: str,
        action_type: str,
        target_entity: str,
        requested_by: str,
        actor_role: str,
        is_dry_run: bool = False,
        idempotency_key: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        auto_execute_if_allowed: bool = True,
        db: Optional[AsyncSession] = None
    ) -> ResponseActionRecord:
        """
        Validates, checks idempotency, checks cooldown, creates action record,
        evaluates approval requirement, and either transitions to PENDING_APPROVAL
        or executes immediately if permitted.
        """
        handler = response_action_registry.get_action(action_type)
        if not handler:
            raise ValueError(f"Unsupported response action type: '{action_type}'")

        # 1. Server-side target validation
        is_valid, val_err = handler.validate(target_entity, parameters)
        if not is_valid:
            raise ValueError(f"Target validation failed: {val_err}")

        # 2. Idempotency Check
        if idempotency_key and db:
            res_idem = await db.execute(
                select(IdempotencyRecord).where(IdempotencyRecord.idempotency_key == idempotency_key)
            )
            idem = res_idem.scalar_one_or_none()
            if idem:
                logger.info("Idempotency key '%s' matched. Returning existing action record %s",
                            idempotency_key, idem.action_id)
                res_act = await db.execute(
                    select(ResponseActionRecord).where(ResponseActionRecord.id == idem.action_id)
                )
                existing_act = res_act.scalar_one_or_none()
                if existing_act:
                    return existing_act

        # 3. Incident & Cooldown Check
        res_inc = await db.execute(select(Incident).where(Incident.id == incident_id))
        inc = res_inc.scalar_one_or_none()
        if not inc:
            raise LookupError(f"Incident '{incident_id}' not found.")

        # Cooldown verification: check recent actions on the same target within cooldown window
        policy_eval = await ResponsePolicyEngine.evaluate(
            risk_score=inc.risk_score,
            severity=inc.severity,
            requested_action=action_type,
            db=db
        )

        if not policy_eval["is_allowed"]:
            raise PermissionError(f"Response policy denied action: {policy_eval['reason']}")

        cooldown_secs = policy_eval.get("cooldown_seconds", 180)
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=cooldown_secs)

        res_recent = await db.execute(
            select(ResponseActionRecord).where(
                ResponseActionRecord.incident_id == incident_id,
                ResponseActionRecord.target_entity == target_entity,
                ResponseActionRecord.action_type == action_type,
                ResponseActionRecord.status.in_(["EXECUTING", "VERIFYING", "SUCCEEDED"]),
                ResponseActionRecord.created_at >= cutoff_time
            )
        )
        if res_recent.scalar_one_or_none():
            raise ValueError(f"Action '{action_type}' on '{target_entity}' is currently in cooldown ({cooldown_secs}s).")

        # 4. Form Action Record
        action_id = str(uuid.uuid4())
        initial_status = "PENDING_APPROVAL" if policy_eval["requires_approval"] else "APPROVED"

        act_record = ResponseActionRecord(
            id=action_id,
            incident_id=incident_id,
            action_type=action_type,
            target_type="IP" if "IP" in action_type else ("HOST" if "HOST" in action_type else "ASSET"),
            target_entity=target_entity,
            parameters=parameters or {},
            status=initial_status,
            is_dry_run=is_dry_run,
            idempotency_key=idempotency_key,
            risk_score_at_execution=inc.risk_score,
            requested_by=requested_by
        )
        db.add(act_record)

        # Record Idempotency mapping
        if idempotency_key:
            idem_rec = IdempotencyRecord(
                idempotency_key=idempotency_key,
                action_id=action_id,
                incident_id=incident_id,
                action_type=action_type,
                target_entity=target_entity
            )
            db.add(idem_rec)

        # Audit Log
        audit = ResponseAuditLog(
            action_id=action_id,
            incident_id=incident_id,
            actor=requested_by,
            actor_role=actor_role,
            action_name=action_type,
            target_entity=target_entity,
            decision=policy_eval["decision"],
            result=initial_status,
            details={"policy": policy_eval.get("matched_policy_name"), "is_dry_run": is_dry_run}
        )
        db.add(audit)

        # Timeline Event
        tl = IncidentTimelineEvent(
            incident_id=incident_id,
            event_type="REMEDIATION",
            title=f"Response Requested: {action_type}",
            description=f"Action '{action_type}' requested for '{target_entity}'. Status: {initial_status}.",
            actor=requested_by,
            metadata_payload={"action_id": action_id, "status": initial_status, "is_dry_run": is_dry_run}
        )
        db.add(tl)
        await db.commit()
        await db.refresh(act_record)

        # 5. If pre-approved and auto_execute requested, trigger immediate execution
        if initial_status == "APPROVED" and auto_execute_if_allowed:
            await cls.execute_action(act_record.id, executed_by=requested_by, db=db)
            await db.refresh(act_record)

        return act_record

    @classmethod
    async def approve_action(
        cls,
        action_id: str,
        approved_by: str,
        approver_role: str,
        db: AsyncSession
    ) -> ResponseActionRecord:
        """Approves a pending response action and initiates execution."""
        norm_role = normalize_role(approver_role)
        if norm_role not in ["admin", "analyst"]:
            raise PermissionError("Viewer role is not authorized to approve response actions.")

        res = await db.execute(select(ResponseActionRecord).where(ResponseActionRecord.id == action_id))
        act = res.scalar_one_or_none()
        if not act:
            raise LookupError(f"Response action '{action_id}' not found.")

        if act.status != "PENDING_APPROVAL":
            raise ValueError(f"Action in status '{act.status}' cannot be approved.")

        act.status = "APPROVED"
        act.approved_by = approved_by
        act.updated_at = datetime.now(timezone.utc)

        audit = ResponseAuditLog(
            action_id=act.id,
            incident_id=act.incident_id,
            actor=approved_by,
            actor_role=approver_role,
            action_name=act.action_type,
            target_entity=act.target_entity,
            decision="APPROVED",
            result="APPROVED",
            details={"approved_by": approved_by}
        )
        db.add(audit)
        await db.commit()
        await db.refresh(act)

        # Trigger execution
        await cls.execute_action(act.id, executed_by=approved_by, db=db)
        await db.refresh(act)
        return act

    @classmethod
    async def reject_action(
        cls,
        action_id: str,
        rejected_by: str,
        reason: str,
        db: AsyncSession
    ) -> ResponseActionRecord:
        """Rejects a pending response action."""
        res = await db.execute(select(ResponseActionRecord).where(ResponseActionRecord.id == action_id))
        act = res.scalar_one_or_none()
        if not act:
            raise LookupError(f"Response action '{action_id}' not found.")

        if act.status != "PENDING_APPROVAL":
            raise ValueError(f"Action in status '{act.status}' cannot be rejected.")

        act.status = "REJECTED"
        act.failure_reason = reason
        act.updated_at = datetime.now(timezone.utc)

        tl = IncidentTimelineEvent(
            incident_id=act.incident_id,
            event_type="REMEDIATION",
            title=f"Response Rejected: {act.action_type}",
            description=f"Action '{act.action_type}' was rejected by {rejected_by}. Reason: {reason}",
            actor=rejected_by,
            metadata_payload={"action_id": act.id, "reason": reason}
        )
        db.add(tl)
        await db.commit()
        await db.refresh(act)
        return act

    @classmethod
    async def execute_action(
        cls,
        action_id: str,
        executed_by: str,
        db: AsyncSession
    ) -> ResponseActionRecord:
        """Executes an approved response action and verifies the result."""
        res = await db.execute(select(ResponseActionRecord).where(ResponseActionRecord.id == action_id))
        act = res.scalar_one_or_none()
        if not act:
            raise LookupError(f"Response action '{action_id}' not found.")

        if act.status not in ["APPROVED", "REQUESTED"]:
            raise ValueError(f"Action in status '{act.status}' cannot be executed directly.")

        handler = response_action_registry.get_action(act.action_type)
        if not handler:
            act.status = "BLOCKED"
            act.failure_reason = "Action handler unavailable."
            await db.commit()
            return act

        # Transition: EXECUTING
        act.status = "EXECUTING"
        await db.flush()

        # Dry-run vs real execution
        if act.is_dry_run:
            exec_res = handler.preview(act.target_entity, act.parameters)
            act.status = "SUCCEEDED"
            act.execution_result = exec_res
            act.verification_result = {"verified": True, "message": "Dry-run simulation verified."}
        else:
            # Real Execution
            exec_res = await handler.execute(act.target_entity, act.parameters)
            act.execution_result = exec_res

            if exec_res.get("status") == "SUCCESS":
                # Transition: VERIFYING
                act.status = "VERIFYING"
                await db.flush()

                is_verified, v_msg = await handler.verify(act.target_entity, exec_res)
                act.verification_result = {"verified": is_verified, "message": v_msg}

                if is_verified:
                    act.status = "SUCCEEDED"
                else:
                    act.status = "FAILED"
                    act.failure_reason = f"Execution succeeded but verification failed: {v_msg}"
            else:
                act.status = "FAILED"
                act.failure_reason = exec_res.get("failure_reason", "Action execution failed.")

        # Update parent Incident
        res_inc = await db.execute(select(Incident).where(Incident.id == act.incident_id))
        inc = res_inc.scalar_one_or_none()
        if inc and act.status == "SUCCEEDED":
            if inc.status in ["OPEN", "DETECTED", "TRIAGED", "INVESTIGATING"]:
                inc.status = "CONTAINED"
            inc.remediation_action = f"{act.action_type} on {act.target_entity} ({'DRY_RUN' if act.is_dry_run else 'EXECUTED'})"

        # Record Timeline event
        tl = IncidentTimelineEvent(
            incident_id=act.incident_id,
            event_type="REMEDIATION",
            title=f"Response {act.status}: {act.action_type}",
            description=f"Action '{act.action_type}' on '{act.target_entity}' resulted in {act.status}.",
            actor=executed_by,
            metadata_payload={"action_id": act.id, "result": act.execution_result, "verification": act.verification_result}
        )
        db.add(tl)
        await db.commit()
        await db.refresh(act)
        return act

    @classmethod
    async def rollback_action(
        cls,
        action_id: str,
        rolled_back_by: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Rolls back an executed action record."""
        return await ResponseRollbackService.rollback_action(
            action_record_id=action_id,
            rolled_back_by=rolled_back_by,
            action_registry=response_action_registry,
            db=db
        )

    @classmethod
    async def get_statistics(cls, db: AsyncSession) -> Dict[str, Any]:
        """Calculates aggregated SOAR response operations statistics."""
        res_status = await db.execute(
            select(ResponseActionRecord.status, func.count(ResponseActionRecord.id)).group_by(ResponseActionRecord.status)
        )
        status_counts = dict(res_status.all())

        res_actions = await db.execute(
            select(ResponseActionRecord.action_type, func.count(ResponseActionRecord.id)).group_by(ResponseActionRecord.action_type)
        )
        action_counts = dict(res_actions.all())

        total = sum(status_counts.values())
        successful = status_counts.get("SUCCEEDED", 0)
        success_rate = round((successful / max(total, 1)) * 100.0, 2)

        return {
            "total_actions": total,
            "success_rate_percentage": success_rate,
            "by_status": status_counts,
            "by_action_type": action_counts,
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
