"""
backend/app/api/v1/response.py
==============================
Phase 3.7 Autonomous SOAR Response, Remediation, and Policy REST Endpoints.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.response import ResponseActionRecord, ResponsePolicy, ResponseAuditLog
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.services.response_orchestrator import ResponseOrchestrator
from backend.app.services.response_decision_service import ResponseDecisionService
from backend.app.services.response_policy_service import ResponsePolicyEngine

router = APIRouter(prefix="/response", tags=["SOAR Response & Remediation Engine"])


# ==============================================================================
# SCHEMAS
# ==============================================================================

class ResponseEvaluateRequest(BaseModel):
    incident_id: str
    risk_score: float = 50.0
    severity: str = "HIGH"
    attack_type: str = "Threat Activity"
    asset_criticality: str = "MEDIUM"
    has_lateral_movement: bool = False
    matched_iocs_count: int = 0
    crown_jewel_index: float = 0.0
    blast_radius_score: float = 0.0
    source_ip: str = "0.0.0.0"
    destination_ip: str = "0.0.0.0"
    target_asset_id: Optional[str] = None


class ActionPreviewRequest(BaseModel):
    incident_id: str
    action_type: str
    target_entity: str
    parameters: Optional[Dict[str, Any]] = None


class ActionSubmitRequest(BaseModel):
    incident_id: str
    action_type: str
    target_entity: str
    is_dry_run: bool = False
    parameters: Optional[Dict[str, Any]] = None


class ActionRejectRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class PolicyCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    enabled: bool = True
    minimum_risk_score: float = 50.0
    minimum_severity: str = "HIGH"
    allowed_actions: List[str] = []
    requires_approval: bool = True
    cooldown_seconds: int = 300
    max_actions_per_incident: int = 5
    allowed_target_types: List[str] = ["IP", "HOST", "ASSET", "USER"]


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.post("/evaluate", summary="Evaluate Incident Response Strategy & Policy")
async def evaluate_response(
    payload: ResponseEvaluateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Evaluates multi-signal incident indicators to recommend response actions and approval requirements."""
    return await ResponseDecisionService.evaluate_incident_response(
        incident_id=payload.incident_id,
        risk_score=payload.risk_score,
        severity=payload.severity,
        attack_type=payload.attack_type,
        asset_criticality=payload.asset_criticality,
        has_lateral_movement=payload.has_lateral_movement,
        matched_iocs_count=payload.matched_iocs_count,
        crown_jewel_index=payload.crown_jewel_index,
        blast_radius_score=payload.blast_radius_score,
        source_ip=payload.source_ip,
        destination_ip=payload.destination_ip,
        target_asset_id=payload.target_asset_id,
        db=db
    )


@router.post("/actions/preview", summary="Generate Dry-Run Simulation Preview")
@router.post("/execute-dryrun", summary="Generate Dry-Run Simulation Preview Alias")
async def preview_action_endpoint(
    payload: ActionPreviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Generates dry-run simulation preview without executing real infrastructure changes."""
    try:
        return await ResponseOrchestrator.preview_action(
            incident_id=payload.incident_id,
            action_type=payload.action_type,
            target_entity=payload.target_entity,
            parameters=payload.parameters,
            db=db
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/actions", summary="Submit and Trigger Response Action", status_code=status.HTTP_201_CREATED)
@router.post("/request", summary="Submit and Trigger Response Action Alias", status_code=status.HTTP_201_CREATED)
async def submit_action_endpoint(
    payload: ActionSubmitRequest,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Submits a response action with idempotency protection and cooldown verification."""
    try:
        act = await ResponseOrchestrator.submit_action(
            incident_id=payload.incident_id,
            action_type=payload.action_type,
            target_entity=payload.target_entity,
            requested_by=current_user.username,
            actor_role=current_user.role,
            is_dry_run=payload.is_dry_run,
            idempotency_key=x_idempotency_key,
            parameters=payload.parameters,
            db=db
        )
        return {
            "id": act.id,
            "incident_id": act.incident_id,
            "action_type": act.action_type,
            "target_entity": act.target_entity,
            "status": act.status,
            "is_dry_run": act.is_dry_run,
            "execution_result": act.execution_result,
            "verification_result": act.verification_result,
            "created_at": act.created_at.isoformat()
        }
    except (ValueError, LookupError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/actions", summary="List Response Actions with Pagination")
@router.get("/requests", summary="List Response Requests Alias")
async def list_actions_endpoint(
    incident_id: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Lists response action execution records with server-side filters."""
    query = select(ResponseActionRecord)
    if incident_id:
        query = query.where(ResponseActionRecord.incident_id == incident_id)
    if status_filter:
        query = query.where(ResponseActionRecord.status == status_filter.upper())

    query = query.order_by(desc(ResponseActionRecord.created_at)).offset(offset).limit(limit)
    res = await db.execute(query)
    items = res.scalars().all()

    return [
        {
            "id": a.id,
            "incident_id": a.incident_id,
            "action_type": a.action_type,
            "target_entity": a.target_entity,
            "status": a.status,
            "is_dry_run": a.is_dry_run,
            "requested_by": a.requested_by,
            "approved_by": a.approved_by,
            "execution_result": a.execution_result,
            "verification_result": a.verification_result,
            "rollback_status": a.rollback_status,
            "failure_reason": a.failure_reason,
            "created_at": a.created_at.isoformat(),
            "updated_at": a.updated_at.isoformat()
        }
        for a in items
    ]


@router.get("/actions/{action_id}", summary="Get Detailed Response Action Record")
async def get_action_details(
    action_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Retrieves full details of a specific response action record."""
    res = await db.execute(select(ResponseActionRecord).where(ResponseActionRecord.id == action_id))
    act = res.scalar_one_or_none()
    if not act:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Response action record not found.")

    return {
        "id": act.id,
        "incident_id": act.incident_id,
        "action_type": act.action_type,
        "target_entity": act.target_entity,
        "status": act.status,
        "is_dry_run": act.is_dry_run,
        "requested_by": act.requested_by,
        "approved_by": act.approved_by,
        "execution_result": act.execution_result,
        "verification_result": act.verification_result,
        "rollback_status": act.rollback_status,
        "failure_reason": act.failure_reason,
        "created_at": act.created_at.isoformat(),
        "updated_at": act.updated_at.isoformat()
    }


@router.post("/actions/{action_id}/approve", summary="Approve Pending Response Action")
@router.post("/approve/{action_id}", summary="Approve Pending Response Action Alias")
async def approve_action_endpoint(
    action_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Approves and executes a pending response action."""
    try:
        act = await ResponseOrchestrator.approve_action(
            action_id=action_id,
            approved_by=current_user.username,
            approver_role=current_user.role,
            db=db
        )
        return {
            "status": "SUCCESS",
            "action_id": act.id,
            "current_status": act.status,
            "approved_by": act.approved_by,
            "verification_result": act.verification_result
        }
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/actions/{action_id}/reject", summary="Reject Pending Response Action")
@router.post("/reject/{action_id}", summary="Reject Pending Response Action Alias")
async def reject_action_endpoint(
    action_id: str,
    payload: ActionRejectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Rejects a pending response action with justification."""
    try:
        act = await ResponseOrchestrator.reject_action(
            action_id=action_id,
            rejected_by=current_user.username,
            reason=payload.reason,
            db=db
        )
        return {
            "status": "SUCCESS",
            "action_id": act.id,
            "current_status": act.status,
            "reason": act.failure_reason
        }
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/actions/{action_id}/execute", summary="Execute Approved Response Action")
async def execute_action_endpoint(
    action_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Triggers execution for an approved response action."""
    try:
        act = await ResponseOrchestrator.execute_action(
            action_id=action_id,
            executed_by=current_user.username,
            db=db
        )
        return {
            "status": "SUCCESS",
            "action_id": act.id,
            "current_status": act.status,
            "execution_result": act.execution_result,
            "verification_result": act.verification_result
        }
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/actions/{action_id}/rollback", summary="Rollback Executed Response Action")
async def rollback_action_endpoint(
    action_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Rolls back an executed action, restoring target infrastructure to prior state."""
    try:
        res = await ResponseOrchestrator.rollback_action(
            action_id=action_id,
            rolled_back_by=current_user.username,
            db=db
        )
        return res
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/actions/{action_id}/audit", summary="Get Audit Trail for Response Action")
async def get_action_audit(
    action_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Retrieves immutable audit logs associated with a response action."""
    res = await db.execute(
        select(ResponseAuditLog).where(ResponseAuditLog.action_id == action_id).order_by(ResponseAuditLog.timestamp.asc())
    )
    logs = res.scalars().all()
    return [
        {
            "id": l.id,
            "action_id": l.action_id,
            "actor": l.actor,
            "actor_role": l.actor_role,
            "action_name": l.action_name,
            "decision": l.decision,
            "result": l.result,
            "details": l.details,
            "timestamp": l.timestamp.isoformat()
        }
        for l in logs
    ]


@router.get("/policies", summary="List Active Response Policies")
async def list_policies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Returns active response policies."""
    return await ResponsePolicyEngine.get_active_policies(db=db)


@router.post("/policies", summary="Create or Update Response Policy", status_code=status.HTTP_201_CREATED)
async def create_policy(
    payload: PolicyCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Creates a new centralized response policy (Admin Only)."""
    pol = ResponsePolicy(
        id=str(uuid.uuid4()),
        name=payload.name,
        description=payload.description,
        enabled=payload.enabled,
        minimum_risk_score=payload.minimum_risk_score,
        minimum_severity=payload.minimum_severity,
        allowed_actions=payload.allowed_actions,
        requires_approval=payload.requires_approval,
        cooldown_seconds=payload.cooldown_seconds,
        max_actions_per_incident=payload.max_actions_per_incident,
        allowed_target_types=payload.allowed_target_types
    )
    db.add(pol)
    await db.commit()
    await db.refresh(pol)
    return {
        "status": "SUCCESS",
        "id": pol.id,
        "name": pol.name
    }


@router.get("/statistics", summary="Get Aggregated SOAR Operations Statistics")
async def get_response_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Returns real-time remediation success rates and action distributions."""
    return await ResponseOrchestrator.get_statistics(db=db)


# ==============================================================================
# LEGACY BACKWARD-COMPATIBLE WORKFLOW ENDPOINTS (PHASE 3.0-3.3)
# ==============================================================================

class ActionRequestPayload(BaseModel):
    incident_id: str
    requested_action: str = Field(..., description="Action: NOTIFY_ANALYST, CREATE_TICKET, ESCALATE_INCIDENT, BLOCK_IOC_SIMULATION, ISOLATE_ASSET_SIMULATION, DISABLE_ACCOUNT_SIMULATION")
    target_entity: str
    parameters: Optional[Dict[str, Any]] = None


class RejectPayload(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class DirectDryRunPayload(BaseModel):
    incident_id: str
    action_type: str
    target_entity: str
    parameters: Optional[Dict[str, Any]] = None


@router.get("/requests", summary="List Response Approval Requests")
async def list_response_requests(
    status_filter: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Lists response approval requests with audit status."""
    reqs = await ResponseOrchestrator.list_requests(status_filter=status_filter, limit=limit, db=db)
    return [
        {
            "id": r.id,
            "incident_id": r.incident_id,
            "requested_action": r.requested_action,
            "target_entity": r.target_entity,
            "parameters": r.parameters,
            "requested_by": r.requested_by,
            "requested_at": r.requested_at.isoformat() if r.requested_at else None,
            "approved_by": r.approved_by,
            "approved_at": r.approved_at.isoformat() if r.approved_at else None,
            "rejected_by": r.rejected_by,
            "rejected_at": r.rejected_at.isoformat() if r.rejected_at else None,
            "status": r.status,
            "reason": r.reason,
            "is_dry_run": r.is_dry_run,
            "execution_id": r.execution_id,
            "audit_id": r.audit_id
        }
        for r in reqs
    ]


@router.post("/request", summary="Submit Action Approval Request", status_code=status.HTTP_201_CREATED)
async def submit_response_request(
    payload: ActionRequestPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Submits a response action for two-tier approval (Analyst/Admin)."""
    try:
        req = await ResponseOrchestrator.request_action(
            incident_id=payload.incident_id,
            requested_action=payload.requested_action,
            target_entity=payload.target_entity,
            requested_by=current_user.username,
            parameters=payload.parameters,
            db=db
        )
        return {
            "status": "SUCCESS",
            "approval_id": req.id,
            "incident_id": req.incident_id,
            "action": req.requested_action,
            "target": req.target_entity,
            "is_dry_run": req.is_dry_run,
            "approval_status": req.status,
            "message": "Action approval request submitted successfully. Awaiting Admin authorization."
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/approve/{approval_id}", summary="Approve and Execute Response Action (Admin Only)")
async def approve_response_request(
    approval_id: str,
    force_live: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Approves and executes a requested SOAR response action. Restricted to Admin."""
    try:
        return await ResponseOrchestrator.approve_and_execute(
            approval_id=approval_id,
            approved_by=current_user.username,
            approver_role=current_user.role,
            force_live=force_live,
            db=db
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reject/{approval_id}", summary="Reject Response Action (Admin Only)")
async def reject_response_request(
    approval_id: str,
    payload: RejectPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Rejects a pending response action request. Restricted to Admin."""
    try:
        req = await ResponseOrchestrator.reject_request(
            approval_id=approval_id,
            rejected_by=current_user.username,
            approver_role=current_user.role,
            reason=payload.reason,
            db=db
        )
        return {
            "status": "SUCCESS",
            "approval_id": req.id,
            "approval_status": req.status,
            "reason": req.reason,
            "rejected_by": req.rejected_by
        }
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/dry-run", summary="Direct Dry Run Execution (Analyst/Admin)")
async def direct_dry_run(
    payload: DirectDryRunPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Executes a non-destructive dry-run simulation of an automated security playbook."""
    try:
        from backend.app.services.playbook_service import PlaybookService
        res = await PlaybookService.execute_action(
            incident_id=payload.incident_id,
            playbook_name=f"DRYRUN_{payload.action_type}",
            action_type=payload.action_type,
            target_entity=payload.target_entity,
            is_dry_run=True,
            executed_by=current_user.username,
            parameters=payload.parameters or {},
            db=db
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

