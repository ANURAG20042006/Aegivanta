"""
backend/app/api/v1/ai_soc_ueba.py
=================================
Phase 37 AI SOC Autonomy, Insider Threat Defense & UEBA 2.0 API Router.
Exposes:
- AI SOC Autonomy & UEBA Posture Scorecard
- UEBA User & Entity Risk Profiles
- Autonomous AI SOC Investigations & Hypotheses
- Trigger Autonomous Investigation
- Human-in-the-Loop Decision Action Approval
- Insider Threat Indicators & Data Hoarding Matrix
- Decision Tracing & Action Audit Trail
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext, get_enforced_tenant_id
from backend.app.services.ueba_scoring_service import UEBAScoringService
from backend.app.services.ai_soc_autonomous_investigator import AISOCAutonomousInvestigator
from backend.app.services.insider_threat_detector_service import InsiderThreatDetectorService
from backend.app.services.ai_soc_posture_service import AISOCPostureService

router = APIRouter(prefix="/ai-soc-ueba", tags=["Phase 37 - AI SOC Autonomy & UEBA 2.0"])


# ==================== Request Payloads ====================

class TriggerInvestigationRequest(BaseModel):
    alert_id: str = Field(..., example="ALT-99201")
    alert_title: str = Field(..., example="Anomalous Large S3 Exfiltration")


class ApproveActionRequest(BaseModel):
    investigation_id: str = Field(..., example="inv-uuid")
    action: str = Field(..., example="Quarantine Endpoint & Invalidate SSO Session")
    acted_by: str = Field(default="lead_soc_analyst", example="lead_soc_analyst")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get AI SOC Autonomy & UEBA Posture Scorecard")
async def get_ai_soc_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates consolidated AI SOC autonomy score and key metrics."""
    tenant_id = get_enforced_tenant_id(context)
    return await AISOCPostureService.get_summary(db=db, tenant_id=tenant_id)


# Profiles
@router.get("/profiles", summary="List UEBA User & Entity Risk Profiles")
async def list_profiles(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists UEBA user risk profiles."""
    tenant_id = get_enforced_tenant_id(context)
    return await UEBAScoringService.list_profiles(db=db, tenant_id=tenant_id, limit=limit)


# Investigations
@router.get("/investigations", summary="List Autonomous AI SOC Investigations")
async def list_investigations(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists autonomous AI SOC investigation cases."""
    tenant_id = get_enforced_tenant_id(context)
    return await AISOCAutonomousInvestigator.list_investigations(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/investigations/trigger", summary="Trigger Autonomous Investigation on Alert")
async def trigger_investigation(
    req: TriggerInvestigationRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Launches an autonomous AI SOC investigation on a trigger alert."""
    tenant_id = get_enforced_tenant_id(context)
    return await AISOCAutonomousInvestigator.trigger_investigation(
        db=db,
        tenant_id=tenant_id,
        alert_id=req.alert_id,
        alert_title=req.alert_title
    )


@router.post("/investigations/approve-action", summary="Approve & Enforce Proposed AI Action")
async def approve_action(
    req: ApproveActionRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Records human-in-the-loop approval and execution audit for an AI proposed action."""
    tenant_id = get_enforced_tenant_id(context)
    return await AISOCAutonomousInvestigator.approve_decision_action(
        db=db,
        tenant_id=tenant_id,
        investigation_id=req.investigation_id,
        action=req.action,
        acted_by=req.acted_by
    )


# Insider Threats
@router.get("/insider-threats", summary="List Insider Threat Indicators")
async def list_insider_threats(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists detected insider threat indicators."""
    tenant_id = get_enforced_tenant_id(context)
    return await InsiderThreatDetectorService.list_insider_threats(db=db, tenant_id=tenant_id, limit=limit)


# Decision Audits
@router.get("/decision-audits", summary="List AI SOC Decision Audits")
async def list_decision_audits(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists AI SOC decision traces and human approval audits."""
    tenant_id = get_enforced_tenant_id(context)
    return await AISOCAutonomousInvestigator.list_decision_audits(db=db, tenant_id=tenant_id, limit=limit)
