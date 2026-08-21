"""
backend/app/api/v1/enterprise_iam.py
===================================
Phase 28 Enterprise Identity, Access Management & Zero Trust 2.0 API Router.
Exposes:
- Unified Identity & Zero Trust Summary Scorecard
- Privileged Access Management (PAM) JIT Elevation Requests, Approvals & Revocations
- Identity Threat Detection & Response (ITDR) Alerts & Simulation
- Continuous Zero Trust Adaptive Authorization Verdicts
- FIDO2 / WebAuthn Passkeys Registry
- Identity Governance Scorecards & Dormant Account Reaper
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.pam_service import PAMService
from backend.app.services.itdr_service import ITDRService
from backend.app.services.zero_trust_continuous_auth_service import ZeroTrustContinuousAuthService
from backend.app.services.identity_governance_service import IdentityGovernanceService

router = APIRouter(prefix="/iam", tags=["Phase 28 - Enterprise IAM, PAM & Zero Trust 2.0"])


# ==================== Request Payloads ====================

class JITElevationRequest(BaseModel):
    user_id: str = Field(default="usr-current", example="usr-current")
    username: str = Field(..., example="sarah.connor@aegivanta.io")
    target_role: str = Field(..., example="CLUSTER_ADMIN")
    target_resource: str = Field(..., example="PROD_K8S_PRIMARY")
    justification: str = Field(..., example="Emergency incident triage for INC-901")
    duration_minutes: int = Field(default=60, ge=5, le=480)


class ITDRSimulationRequest(BaseModel):
    threat_type: str = Field(default="MFA_FATIGUE", example="MFA_FATIGUE")
    target_username: str = Field(default="john.doe@aegivanta.io", example="john.doe@aegivanta.io")
    source_ip: str = Field(default="198.51.100.77", example="198.51.100.77")


class ZeroTrustEvaluationRequest(BaseModel):
    username: str = Field(..., example="sarah.connor@aegivanta.io")
    identity_risk_score: float = Field(default=20.0, ge=0.0, le=100.0)
    device_trust_score: float = Field(default=95.0, ge=0.0, le=100.0)
    resource_criticality: str = Field(default="HIGH", example="HIGH")
    is_known_location: bool = Field(default=True)
    is_managed_device: bool = Field(default=True)


class DormantReapRequest(BaseModel):
    inactivity_days_threshold: int = Field(default=90, ge=30, le=365)


# ==================== Endpoints ====================

@router.get("/summary", summary="Get Unified Identity & Zero Trust Scorecard")
async def get_iam_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates unified IAM & Zero Trust 2.0 posture score and key metrics."""
    tenant_id = context.tenant_id or "default-tenant"
    return await IdentityGovernanceService.get_iam_summary(db=db, tenant_id=tenant_id)


# PAM Endpoints
@router.get("/pam/elevations", summary="List JIT Privilege Elevations")
async def list_pam_elevations(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists PAM JIT elevation requests and active sessions."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PAMService.list_elevations(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/pam/request-elevation", summary="Request JIT Privilege Elevation")
async def request_jit_elevation(
    req: JITElevationRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Submits a JIT privilege elevation request."""
    tenant_id = context.tenant_id or "default-tenant"
    elevation = await PAMService.request_elevation(
        db=db,
        tenant_id=tenant_id,
        user_id=req.user_id,
        username=req.username,
        target_role=req.target_role,
        target_resource=req.target_resource,
        justification=req.justification,
        duration_minutes=req.duration_minutes
    )
    return {
        "id": elevation.id,
        "username": elevation.username,
        "target_role": elevation.target_role,
        "status": elevation.status,
        "duration_minutes": elevation.duration_minutes
    }


@router.post("/pam/approve/{id}", summary="Approve JIT Privilege Elevation")
async def approve_jit_elevation(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Approves and activates a JIT elevation."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PAMService.approve_elevation(db=db, tenant_id=tenant_id, elevation_id=id)


@router.post("/pam/revoke/{id}", summary="Revoke JIT Privilege Elevation")
async def revoke_jit_elevation(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Terminates an active JIT elevation."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PAMService.revoke_elevation(db=db, tenant_id=tenant_id, elevation_id=id)


# ITDR Endpoints
@router.get("/itdr/detections", summary="List ITDR Threat Detections")
async def list_itdr_detections(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists identity threat detections (MFA fatigue, password spray, impossible travel)."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ITDRService.list_detections(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/itdr/simulate-attack", summary="Simulate Identity Threat Attack")
async def simulate_itdr_attack(
    req: ITDRSimulationRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Simulates an identity attack vector for ITDR validation."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ITDRService.simulate_identity_attack(
        db=db,
        tenant_id=tenant_id,
        threat_type=req.threat_type,
        target_username=req.target_username,
        source_ip=req.source_ip
    )


# Zero Trust Continuous Auth
@router.post("/zero-trust/evaluate-session", summary="Evaluate Continuous Zero Trust Authorization")
async def evaluate_zero_trust_session(
    req: ZeroTrustEvaluationRequest
):
    """Evaluates session risk factors and returns real-time access authorization verdict."""
    return ZeroTrustContinuousAuthService.evaluate_session_access(
        username=req.username,
        identity_risk_score=req.identity_risk_score,
        device_trust_score=req.device_trust_score,
        resource_criticality=req.resource_criticality,
        is_known_location=req.is_known_location,
        is_managed_device=req.is_managed_device
    )


# Passkeys & Governance
@router.get("/passkeys", summary="List Registered Passkeys")
async def list_registered_passkeys(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists registered FIDO2 / WebAuthn Passkeys."""
    tenant_id = context.tenant_id or "default-tenant"
    return await IdentityGovernanceService.list_passkeys(db=db, tenant_id=tenant_id)


@router.get("/governance/scorecards", summary="List Identity Risk Scorecards")
async def list_identity_scorecards(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists per-user identity posture scorecards and privilege creep status."""
    tenant_id = context.tenant_id or "default-tenant"
    return await IdentityGovernanceService.list_scorecards(db=db, tenant_id=tenant_id)


@router.post("/governance/reap-dormant", summary="Reap Inactive Dormant Identities")
async def reap_dormant_identities(
    req: DormantReapRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Identifies and reaps accounts inactive for greater than the threshold days."""
    tenant_id = context.tenant_id or "default-tenant"
    return await IdentityGovernanceService.reap_dormant_identities(
        db=db,
        tenant_id=tenant_id,
        inactivity_days_threshold=req.inactivity_days_threshold
    )
