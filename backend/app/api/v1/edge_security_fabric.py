"""
backend/app/api/v1/edge_security_fabric.py
=========================================
Phase 41 Global Distributed Edge Security & Regional Ingestion Fabric API Router.
Exposes:
- Global Edge Posture Scorecard
- Distributed Edge PoP Fleet Registry
- Edge Inspection & DDoS Scrubbing Policies
- Regional Ingestion & WAN Replication Routing
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.edge_fabric_service import EdgeFabricService
from backend.app.services.edge_inspection_service import EdgeInspectionService
from backend.app.services.edge_security_posture_service import EdgeSecurityPostureService

router = APIRouter(prefix="/edge-fabric", tags=["Phase 41 - Distributed Edge Security Fabric"])


# ==================== Request Payloads ====================

class CreateEdgePolicyRequest(BaseModel):
    policy_name: str = Field(..., example="Global Autonomous L7 DDoS Scrubbing")
    inspection_mode: str = Field(default="INLINE_BLOCK", example="INLINE_BLOCK")
    edge_rate_limit_rps: int = Field(default=50000, example=50000)
    geo_fence_action: str = Field(default="CHALLENGE", example="CHALLENGE")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get Global Edge Security Posture Scorecard")
async def get_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates consolidated edge posture metrics and health scorecard."""
    tenant_id = context.tenant_id or "default-tenant"
    return await EdgeSecurityPostureService.get_summary(db=db, tenant_id=tenant_id)


# PoPs
@router.get("/pops", summary="List Global Edge PoP Ingestion Nodes")
async def list_pops(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active global edge PoP ingestion nodes."""
    tenant_id = context.tenant_id or "default-tenant"
    return await EdgeFabricService.list_pops(db=db, tenant_id=tenant_id, limit=limit)


# Policies
@router.get("/policies", summary="List Edge Inspection & DDoS Policies")
async def list_policies(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active edge inspection policies."""
    tenant_id = context.tenant_id or "default-tenant"
    return await EdgeInspectionService.list_policies(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/policies", summary="Deploy New Edge Inspection Policy")
async def create_policy(
    req: CreateEdgePolicyRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Deploys a new edge inspection & DDoS mitigation policy."""
    tenant_id = context.tenant_id or "default-tenant"
    return await EdgeInspectionService.create_policy(
        db=db,
        tenant_id=tenant_id,
        policy_name=req.policy_name,
        inspection_mode=req.inspection_mode,
        edge_rate_limit_rps=req.edge_rate_limit_rps,
        geo_fence_action=req.geo_fence_action
    )


# Routes
@router.get("/routes", summary="List Regional Ingestion WAN Replication Routes")
async def list_routes(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists regional ingestion routes to primary core clusters."""
    tenant_id = context.tenant_id or "default-tenant"
    return await EdgeFabricService.list_routes(db=db, tenant_id=tenant_id, limit=limit)
