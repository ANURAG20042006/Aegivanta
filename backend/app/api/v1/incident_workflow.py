from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.incident_workflow_service import IncidentWorkflowService
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/incidents", tags=["Incident Workflow & Timeline"])


class TransitionStatusRequest(BaseModel):
    new_status: str
    reason: Optional[str] = None
    notes: Optional[str] = None


class AssignAnalystRequest(BaseModel):
    analyst_username: str


@router.get("/{id}/timeline", summary="Get Immutable Chronological Incident Timeline")
async def get_incident_timeline(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves immutable chronological timeline events for a security incident."""
    return await IncidentWorkflowService.get_incident_timeline(db, id)


@router.post("/{id}/transition", summary="Execute Audited Status Transition")
async def transition_incident_status(
    id: str,
    payload: TransitionStatusRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Executes state machine transition with audited reason and note capture."""
    actor = context.user_id or "ANALYST"
    inc = await IncidentWorkflowService.transition_incident_status(
        db=db,
        incident_id=id,
        new_status=payload.new_status,
        actor=actor,
        reason=payload.reason,
        notes=payload.notes
    )
    return {
        "status": "SUCCESS",
        "incident_id": inc.id,
        "current_status": inc.status,
        "analyst": inc.analyst,
        "resolution": inc.resolution
    }


@router.post("/{id}/assign", summary="Assign Incident to Security Analyst")
async def assign_analyst(
    id: str,
    payload: AssignAnalystRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Assigns primary investigation ownership to an analyst."""
    actor = context.user_id or "ANALYST"
    inc = await IncidentWorkflowService.assign_incident_analyst(
        db=db,
        incident_id=id,
        analyst_username=payload.analyst_username,
        actor=actor
    )
    return {
        "status": "SUCCESS",
        "incident_id": inc.id,
        "assigned_analyst": inc.analyst
    }
