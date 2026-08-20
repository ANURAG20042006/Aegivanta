from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.autonomous_response_service import AutonomousResponseService
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/autonomous-response", tags=["Autonomous Threat Response"])


class UpdatePolicyRequest(BaseModel):
    autonomy_level: str
    is_enabled: Optional[bool] = True
    min_confidence_threshold: Optional[float] = 0.85
    min_risk_threshold: Optional[float] = 70.0
    allowed_actions: Optional[List[str]] = None


class SimulateResponseRequest(BaseModel):
    incident_id: str
    action_type: str
    target_entity: str
    parameters: Optional[Dict[str, Any]] = None


class ExecuteResponseRequest(BaseModel):
    incident_id: str
    action_type: str
    target_entity: str
    bypass_approval: Optional[bool] = False


@router.get("/policy", summary="Get Active Autonomous Response Policy")
async def get_response_policy(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves the active autonomous response policy and autonomy level for the tenant."""
    tenant_id = context.tenant_id or "default-tenant"
    policy = await AutonomousResponseService.get_or_create_tenant_policy(db, tenant_id)
    return {
        "policy_id": policy.id,
        "tenant_id": policy.tenant_id,
        "policy_name": policy.policy_name,
        "autonomy_level": policy.autonomy_level,
        "is_enabled": policy.is_enabled,
        "min_confidence_threshold": policy.min_confidence_threshold,
        "min_risk_threshold": policy.min_risk_threshold,
        "allowed_actions": policy.allowed_actions
    }


@router.put("/policy", summary="Update Autonomous Response Policy & Autonomy Level")
async def update_response_policy(
    payload: UpdatePolicyRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Updates autonomy levels (LEVEL_0_OBSERVE to LEVEL_4_FULL_AUTONOMOUS) and threshold guards."""
    tenant_id = context.tenant_id or "default-tenant"
    policy = await AutonomousResponseService.get_or_create_tenant_policy(db, tenant_id)
    policy.autonomy_level = payload.autonomy_level
    if payload.is_enabled is not None:
        policy.is_enabled = payload.is_enabled
    if payload.min_confidence_threshold is not None:
        policy.min_confidence_threshold = payload.min_confidence_threshold
    if payload.min_risk_threshold is not None:
        policy.min_risk_threshold = payload.min_risk_threshold
    if payload.allowed_actions is not None:
        policy.allowed_actions = payload.allowed_actions

    await db.flush()
    return {"status": "SUCCESS", "autonomy_level": policy.autonomy_level}


@router.post("/simulate", summary="Simulate Autonomous Response (Dry Run)")
async def simulate_response(
    payload: SimulateResponseRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Performs dry-run simulation of response action, computing blast radius and required approvals."""
    tenant_id = context.tenant_id or "default-tenant"
    return await AutonomousResponseService.simulate_response(
        db=db,
        tenant_id=tenant_id,
        incident_id=payload.incident_id,
        action_type=payload.action_type,
        target_entity=payload.target_entity,
        parameters=payload.parameters
    )


@router.post("/execute", summary="Execute or Request Autonomous Response Action")
async def execute_response(
    payload: ExecuteResponseRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Validates policy constraints and executes or queues response action for human approval."""
    tenant_id = context.tenant_id or "default-tenant"
    actor = context.user_id or "AUTONOMOUS_ENGINE"
    return await AutonomousResponseService.execute_response(
        db=db,
        tenant_id=tenant_id,
        incident_id=payload.incident_id,
        action_type=payload.action_type,
        target_entity=payload.target_entity,
        actor=actor,
        bypass_approval=payload.bypass_approval or False
    )


@router.post("/{id}/rollback", summary="Rollback Reversible Autonomous Response Action")
async def rollback_response(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Reverts an executed reversible containment action back to original system state."""
    tenant_id = context.tenant_id or "default-tenant"
    actor = context.user_id or "ADMINISTRATOR"
    return await AutonomousResponseService.rollback_response(
        db=db,
        tenant_id=tenant_id,
        action_id=id,
        actor=actor
    )
