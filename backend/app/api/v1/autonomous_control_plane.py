"""
backend/app/api/v1/autonomous_control_plane.py
==============================================
Phase 49 — Autonomous Cyber Defense Control Plane & Decisive War Room Router.
Exposes:
- Autonomous Control Plane Posture Scorecard
- Autonomous Defense Mission Lifecycle & Directives
- Live Multi-Agent War Room Management & Agent Consensus
- Granular Tactical Intervention Decisions
- Emergency Kill Switch & Human-in-the-Loop Override Controls
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.autonomous_mission_service import AutonomousMissionService
from backend.app.services.defense_war_room_service import DefenseWarRoomService
from backend.app.services.control_plane_posture_service import ControlPlanePostureService

router = APIRouter(
    prefix="/control-plane",
    tags=["Phase 49 - Autonomous Control Plane"]
)


# ==================== Request Payloads ====================

class CreateMissionRequest(BaseModel):
    mission_name: str = Field(..., example="Operation Apex Shield")
    mission_code: str = Field(..., example="MISSION-APEX-09")
    objective: str = Field(..., example="Autonomous containment and threat eradication across cloud VPCs.")
    threat_tier: str = Field(default="CRITICAL", example="CRITICAL")
    autonomy_level: str = Field(default="FULL_AUTONOMY", example="FULL_AUTONOMY")
    blast_radius_limit_usd: float = Field(default=100000.0, example=100000.0)


class KillSwitchRequest(BaseModel):
    activate: bool = Field(..., example=True)


class ExecuteActionRequest(BaseModel):
    action_name: str = Field(..., example="Revoke Compromised IAM Access Token")
    action_category: str = Field(default="CONTAINMENT", example="CONTAINMENT")
    proposing_agent: str = Field(default="Agent-IdentitySentinel", example="Agent-IdentitySentinel")
    target_entity: str = Field(..., example="sa-workload@prod-k8s.iam.internal")


# ==================== Endpoints ====================

@router.get(
    "/summary",
    summary="Control Plane Posture Scorecard",
    description="Returns aggregate posture scorecard for the Autonomous Cyber Defense Control Plane."
)
async def get_control_plane_summary(
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await ControlPlanePostureService.get_control_plane_summary(db=db, tenant_id=ctx.tenant_id)


@router.get(
    "/missions",
    summary="List Autonomous Defense Missions",
    description="Lists all active and completed autonomous defense missions."
)
async def list_missions(
    limit: int = Query(default=20, ge=1, le=100),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    return await AutonomousMissionService.list_missions(db=db, tenant_id=ctx.tenant_id, limit=limit)


@router.post(
    "/missions",
    summary="Launch Autonomous Defense Mission",
    description="Launches a new autonomous cyber defense mission directive with bounded autonomy."
)
async def create_mission(
    payload: CreateMissionRequest = Body(...),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await AutonomousMissionService.create_mission(
        db=db,
        tenant_id=ctx.tenant_id,
        mission_name=payload.mission_name,
        mission_code=payload.mission_code,
        objective=payload.objective,
        threat_tier=payload.threat_tier,
        autonomy_level=payload.autonomy_level,
        blast_radius_limit_usd=payload.blast_radius_limit_usd,
    )


@router.get(
    "/war-rooms",
    summary="List Live War Rooms",
    description="Lists all active multi-agent defense war rooms."
)
async def list_war_rooms(
    limit: int = Query(default=20, ge=1, le=100),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    return await DefenseWarRoomService.list_war_rooms(db=db, tenant_id=ctx.tenant_id, limit=limit)


@router.get(
    "/war-rooms/{war_room_id}",
    summary="Get War Room Details",
    description="Returns live agent consensus, tactical plan, and action history for a war room."
)
async def get_war_room_details(
    war_room_id: str = Path(...),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    return await DefenseWarRoomService.get_war_room_details(
        db=db, tenant_id=ctx.tenant_id, war_room_id=war_room_id
    )


@router.post(
    "/war-rooms/{war_room_id}/kill-switch",
    summary="Toggle War Room Kill Switch",
    description="Emergency intervention to pause or resume autonomous action execution in a war room."
)
async def toggle_kill_switch(
    war_room_id: str = Path(...),
    payload: KillSwitchRequest = Body(...),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await DefenseWarRoomService.toggle_kill_switch(
        db=db,
        tenant_id=ctx.tenant_id,
        war_room_id=war_room_id,
        activate=payload.activate
    )


@router.post(
    "/war-rooms/{war_room_id}/action",
    summary="Execute Tactical Intervention Action",
    description="Records and executes an autonomous or operator-directed tactical action in a war room."
)
async def execute_tactical_action(
    war_room_id: str = Path(...),
    payload: ExecuteActionRequest = Body(...),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await DefenseWarRoomService.execute_tactical_action(
        db=db,
        tenant_id=ctx.tenant_id,
        war_room_id=war_room_id,
        action_name=payload.action_name,
        action_category=payload.action_category,
        proposing_agent=payload.proposing_agent,
        target_entity=payload.target_entity,
    )
