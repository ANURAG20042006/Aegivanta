"""
backend/app/api/v1/playbooks.py
===============================
Automated Playbook Execution & Simulation API Endpoints with Enterprise RBAC.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.playbook import PlaybookExecution
from backend.app.services.playbook_service import PlaybookService

router = APIRouter(prefix="/playbooks", tags=["Security Playbooks & Automation"])

APPROVED_PLAYBOOK_ACTIONS = {
    "BLOCK_IP",
    "QUARANTINE_VLAN",
    "NOTIFY_WEBHOOK",
    "ISOLATE_HOST",
    "COLLECT_PCAP",
    "RESET_SESSION",
    "RATE_LIMIT"
}


class PlaybookExecuteRequest(BaseModel):
    incident_id: str = Field(..., description="Target incident ID")
    playbook_name: str = Field(..., description="Playbook name e.g. IP_CONTAINMENT_PLAYBOOK")
    action_type: str = Field(..., description="Action: BLOCK_IP, QUARANTINE_VLAN, NOTIFY_WEBHOOK, ISOLATE_HOST, COLLECT_PCAP")
    target_entity: str = Field(..., description="Target IP address, hostname, or subnet")
    is_dry_run: bool = Field(True, description="True for simulation mode (default); False for live execution")
    force_live_execution: bool = Field(False, description="Explicit confirmation flag required for live destructive actions")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


@router.get("/executions", summary="List Playbook Execution History")
async def list_playbook_executions(
    incident_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves audit history of all simulated and executed automated playbooks."""
    query = select(PlaybookExecution)
    if incident_id:
        query = query.where(PlaybookExecution.incident_id == incident_id)
    query = query.order_by(PlaybookExecution.created_at.desc()).limit(limit)

    res = await db.execute(query)
    executions = res.scalars().all()
    return [
        {
            "id": e.id,
            "audit_id": getattr(e, "audit_id", e.id),
            "incident_id": e.incident_id,
            "playbook_name": e.playbook_name,
            "action_type": e.action_type,
            "is_dry_run": e.is_dry_run,
            "target_entity": e.target_entity,
            "status": e.status,
            "executed_by": e.executed_by,
            "actor_role": getattr(e, "actor_role", "analyst"),
            "authorization_decision": getattr(e, "authorization_decision", "APPROVED"),
            "execution_log": e.execution_log,
            "created_at": e.created_at.isoformat() if e.created_at else None
        }
        for e in executions
    ]


@router.post("/execute", status_code=status.HTTP_201_CREATED, summary="Execute or Simulate Playbook Action")
async def execute_playbook(
    payload: PlaybookExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """
    Executes a security playbook action with mandatory audit logging and strict RBAC authorization:
      - Viewer: Denied (HTTP 403)
      - Analyst: Authorized strictly for dry-run simulation mode (is_dry_run=True)
      - Admin: Authorized for dry-run and live actions (requires explicit force_live_execution for live)
    """
    action_type = payload.action_type.upper().strip()
    if action_type not in APPROVED_PLAYBOOK_ACTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Action '{payload.action_type}' is not an approved playbook action. Allowed: {sorted(APPROVED_PLAYBOOK_ACTIONS)}"
        )

    # RBAC Authorization Enforcement
    is_dry_run = payload.is_dry_run
    user_role = current_user.role.lower()

    if not is_dry_run:
        # Live execution requested
        if user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is restricted to simulation mode (dry_run=True). Live infrastructure modifications require Administrator privileges."
            )
        if not payload.force_live_execution:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Live execution requires explicit 'force_live_execution=True' confirmation flag to prevent unintentional changes."
            )

    exec_params = dict(payload.parameters or {})
    exec_params["actor_role"] = user_role

    result = await PlaybookService.execute_action(
        incident_id=payload.incident_id,
        playbook_name=payload.playbook_name,
        action_type=action_type,
        target_entity=payload.target_entity,
        is_dry_run=is_dry_run,
        executed_by=current_user.username,
        parameters=exec_params,
        db=db
    )
    await db.commit()
    return result
