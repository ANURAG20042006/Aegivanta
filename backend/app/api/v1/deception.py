"""
backend/app/api/v1/deception.py
===============================
Phase 33 Deception Technology, Honeypots & Active Adversary Engagement API Router.
Exposes:
- Deception Readiness Scorecard & MITRE Engage Summary
- Honeypot Fleet Management & Decoy Deployment
- Canary Token Generator & Trigger Processing Webhooks
- Real-Time Adversary Telemetry & Interaction Ledger
- Endpoint Deception Lure Distribution Map
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext, get_enforced_tenant_id
from backend.app.services.honeypot_fleet_service import HoneypotFleetService
from backend.app.services.canary_token_service import CanaryTokenService
from backend.app.services.adversary_engagement_service import AdversaryEngagementService
from backend.app.services.deception_posture_service import DeceptionPostureService

router = APIRouter(prefix="/deception", tags=["Phase 33 - Deception Technology & Honeypots"])


# ==================== Request Payloads ====================

class DeployHoneypotRequest(BaseModel):
    node_name: str = Field(..., example="decoy-ssh-bastion-02")
    decoy_type: str = Field(default="SSH_COWRIE", example="SSH_COWRIE")
    internal_ip: str = Field(..., example="10.0.12.51")
    vlan_segment: str = Field(default="DMZ-DECEPTION-VLAN")


class GenerateCanaryTokenRequest(BaseModel):
    token_type: str = Field(default="AWS_API_KEY", example="AWS_API_KEY")
    token_name: str = Field(..., example="devops-prod-aws-key")
    placement_description: str = Field(..., example="Placed in /home/ubuntu/.aws/credentials")


class TriggerCanaryRequest(BaseModel):
    source_ip: str = Field(default="198.51.100.22", example="198.51.100.22")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get Deception & Adversary Engagement Scorecard")
async def get_deception_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates consolidated deception posture score and key metrics."""
    tenant_id = get_enforced_tenant_id(context)
    return await DeceptionPostureService.get_summary(db=db, tenant_id=tenant_id)


# Honeypot Fleet
@router.get("/honeypots", summary="List Deployed Honeypots")
async def list_honeypots(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists deployed honeypot decoys across corporate segments."""
    tenant_id = get_enforced_tenant_id(context)
    return await HoneypotFleetService.list_honeypots(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/honeypots/deploy", summary="Deploy New Honeypot Decoy")
async def deploy_honeypot(
    req: DeployHoneypotRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Deploys a new honeypot decoy into target network segment."""
    tenant_id = get_enforced_tenant_id(context)
    return await HoneypotFleetService.deploy_honeypot(
        db=db,
        tenant_id=tenant_id,
        node_name=req.node_name,
        decoy_type=req.decoy_type,
        internal_ip=req.internal_ip,
        vlan_segment=req.vlan_segment
    )


# Canary Tokens
@router.get("/canaries", summary="List Active Canary Tokens")
async def list_canaries(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active canary tokens."""
    tenant_id = get_enforced_tenant_id(context)
    return await CanaryTokenService.list_canary_tokens(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/canaries/generate", summary="Generate Traceable Canary Token")
async def generate_canary_token(
    req: GenerateCanaryTokenRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Generates a new traceable canary token."""
    tenant_id = get_enforced_tenant_id(context)
    return await CanaryTokenService.generate_token(
        db=db,
        tenant_id=tenant_id,
        token_type=req.token_type,
        token_name=req.token_name,
        placement_description=req.placement_description
    )


@router.post("/canaries/trigger/{token_id}", summary="Process Canary Token Trip Ping")
async def trigger_canary_token(
    token_id: str,
    req: TriggerCanaryRequest = Body(default_factory=TriggerCanaryRequest),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Processes a canary token hit and logs high-fidelity interaction event."""
    tenant_id = get_enforced_tenant_id(context)
    res = await CanaryTokenService.process_canary_trigger(
        db=db,
        tenant_id=tenant_id,
        token_id=token_id,
        source_ip=req.source_ip
    )
    return res or {"error": "Token not found"}


# Adversary Interactions
@router.get("/interactions", summary="List Adversary Interaction Ledger")
async def list_interactions(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists captured adversary keystrokes and honeypot interactions."""
    tenant_id = get_enforced_tenant_id(context)
    return await AdversaryEngagementService.list_interactions(db=db, tenant_id=tenant_id, limit=limit)


# Endpoint Lures
@router.get("/endpoint-lures", summary="List Endpoint Deception Lures")
async def list_endpoint_lures(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active deception lures distributed on corporate endpoints."""
    tenant_id = get_enforced_tenant_id(context)
    return await AdversaryEngagementService.list_endpoint_lures(db=db, tenant_id=tenant_id, limit=limit)
