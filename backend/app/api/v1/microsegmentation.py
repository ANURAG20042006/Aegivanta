"""
backend/app/api/v1/microsegmentation.py
=======================================
Phase 36 Microsegmentation, Software-Defined Perimeter (SDP) & ZTNA 2.0 API Router.
Exposes:
- Microsegmentation & ZTNA Posture Scorecard
- SDP Gateway Connector Fleet
- L4/L7 Microsegmentation Policies & Rule Compiler
- Active Identity-Bound ZTNA Client Sessions
- Lateral Movement Interception Alerts
- Network Flow & Segment Mesh Visualizer Graph
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext, get_enforced_tenant_id
from backend.app.services.ztna_controller_service import ZTNAControllerService
from backend.app.services.microsegmentation_policy_service import MicrosegmentationPolicyService
from backend.app.services.lateral_movement_detector_service import LateralMovementDetectorService
from backend.app.services.microsegmentation_posture_service import MicrosegmentationPostureService

router = APIRouter(prefix="/microsegmentation", tags=["Phase 36 - Microsegmentation & ZTNA 2.0"])


# ==================== Request Payloads ====================

class CreatePolicyRequest(BaseModel):
    policy_name: str = Field(..., example="Isolate Payment Core")
    source_segment: str = Field(..., example="PAYMENT_GATEWAY_VPC")
    destination_segment: str = Field(..., example="CORE_DATABASE_CLUSTER")
    protocol_port: str = Field(default="TCP/5432", example="TCP/5432")
    enforcement_action: str = Field(default="ALLOW_ENCRYPTED_TUNNEL", example="ALLOW_ENCRYPTED_TUNNEL")
    min_device_trust_score: int = Field(default=85, example=85)


class TerminateSessionRequest(BaseModel):
    session_id: str = Field(..., example="session-uuid")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get ZTNA & Microsegmentation Posture Scorecard")
async def get_ztna_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates composite ZTNA posture score and key network isolation metrics."""
    tenant_id = get_enforced_tenant_id(context)
    return await MicrosegmentationPostureService.get_summary(db=db, tenant_id=tenant_id)


# Connector Fleet
@router.get("/connectors", summary="List SDP / ZTNA Connector Gateway Nodes")
async def list_connectors(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active SDP / ZTNA gateway connector nodes."""
    tenant_id = get_enforced_tenant_id(context)
    return await ZTNAControllerService.list_connectors(db=db, tenant_id=tenant_id, limit=limit)


# Policies
@router.get("/policies", summary="List Microsegmentation Policies")
async def list_policies(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active L4/L7 microsegmentation policies."""
    tenant_id = get_enforced_tenant_id(context)
    return await MicrosegmentationPolicyService.list_policies(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/policies", summary="Create Microsegmentation Policy")
async def create_policy(
    req: CreatePolicyRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new L4/L7 segment isolation policy."""
    tenant_id = get_enforced_tenant_id(context)
    return await MicrosegmentationPolicyService.create_policy(
        db=db,
        tenant_id=tenant_id,
        policy_name=req.policy_name,
        source_segment=req.source_segment,
        destination_segment=req.destination_segment,
        protocol_port=req.protocol_port,
        enforcement_action=req.enforcement_action,
        min_device_trust_score=req.min_device_trust_score
    )


# Active Sessions
@router.get("/sessions", summary="List Identity-Bound ZTNA Sessions")
async def list_sessions(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active identity-bound ZTNA client access sessions."""
    tenant_id = get_enforced_tenant_id(context)
    return await ZTNAControllerService.list_sessions(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/sessions/terminate", summary="Revoke / Terminate ZTNA Session")
async def terminate_session(
    req: TerminateSessionRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Revokes and terminates an active ZTNA client session."""
    tenant_id = get_enforced_tenant_id(context)
    return await ZTNAControllerService.terminate_session(
        db=db,
        tenant_id=tenant_id,
        session_id=req.session_id
    )


# Lateral Alerts
@router.get("/lateral-alerts", summary="List Intercepted Lateral Movement Alerts")
async def list_lateral_alerts(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists intercepted lateral movement violations."""
    tenant_id = get_enforced_tenant_id(context)
    return await LateralMovementDetectorService.list_lateral_alerts(db=db, tenant_id=tenant_id, limit=limit)


# Network Flow Graph
@router.get("/network-flow-graph", summary="Get Microsegmentation Flow Mesh Graph")
async def get_network_flow_graph():
    """Returns network topology nodes and segment flow links."""
    return LateralMovementDetectorService.get_network_flow_mesh()
