"""
backend/app/api/v1/response.py
==============================
API Endpoints for Controlled SOAR Approval Workflows and Safe Dry-Run Execution.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.core.dependencies import require_role
from backend.app.services.response_orchestrator import ResponseOrchestrator

router = APIRouter(prefix="/response", tags=["Controlled SOAR Orchestration"])


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
            "id": req.id,
            "incident_id": req.incident_id,
            "requested_action": req.requested_action,
            "target_entity": req.target_entity,
            "status": req.status,
            "requested_by": req.requested_by,
            "requested_at": req.requested_at.isoformat() if req.requested_at else None
        }
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.post("/approve/{request_id}", summary="Approve & Execute Response Action")
async def approve_response_request(
    request_id: str,
    force_live: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Approves and executes response action (Admin role strictly required)."""
    try:
        return await ResponseOrchestrator.approve_and_execute(
            approval_id=request_id,
            approved_by=current_user.username,
            approver_role=current_user.role,
            force_live=force_live,
            db=db
        )
    except (ValueError, PermissionError) as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.post("/reject/{request_id}", summary="Reject Response Action Request")
async def reject_response_request(
    request_id: str,
    payload: RejectPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Rejects a pending response approval request."""
    try:
        req = await ResponseOrchestrator.reject_action(
            approval_id=request_id,
            rejected_by=current_user.username,
            approver_role=current_user.role,
            reason=payload.reason,
            db=db
        )
        return {
            "id": req.id,
            "status": req.status,
            "rejected_by": req.rejected_by,
            "reason": req.reason
        }
    except (ValueError, PermissionError) as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.post("/execute-dryrun", summary="Execute Immediate Simulation Dry-Run")
async def execute_direct_dry_run(
    payload: DirectDryRunPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Executes a safe dry-run simulation of a remediation action with audit logging."""
    from backend.app.services.playbook_service import PlaybookService
    result = await PlaybookService.execute_action(
        incident_id=payload.incident_id,
        playbook_name=f"DRYRUN_{payload.action_type}",
        action_type=payload.action_type,
        target_entity=payload.target_entity,
        is_dry_run=True,
        executed_by=current_user.username,
        parameters=payload.parameters or {"actor_role": current_user.role},
        db=db
    )
    return result
