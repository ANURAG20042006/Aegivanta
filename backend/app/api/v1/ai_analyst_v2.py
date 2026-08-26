"""
backend/app/api/v1/ai_analyst_v2.py
===================================
Phase 26.9 & 26.10 AI SOC Analyst V2 & Autonomous Correlation API Endpoints.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext, get_enforced_tenant_id
from backend.app.services.ai_soc_analyst_v2_service import AISOCAnalystV2Service
from backend.app.services.autonomous_correlation_service import AutonomousCorrelationEngine

router = APIRouter(prefix="/ai-analyst/v2", tags=["AI SOC Analyst V2 & Correlation"])


class AIInvestigateRequest(BaseModel):
    query: str = Field(..., example="Analyze the active lateral movement campaign on WKS-EXEC-01.")
    case_id: Optional[str] = None
    incident_id: Optional[str] = None


@router.post("/investigate", summary="Query AI SOC Analyst V2")
async def investigate_with_ai(
    req: AIInvestigateRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes structured AI reasoning over verified empirical evidence with
    prompt injection sanitization and mandatory human approval gating for containment.
    """
    tenant_id = get_enforced_tenant_id(context)
    return await AISOCAnalystV2Service.analyze_security_context(
        db=db,
        tenant_id=tenant_id,
        analyst_query=req.query,
        case_id=req.case_id,
        incident_id=req.incident_id
    )


@router.get("/correlation/{incident_id}", summary="Get Explainable Multi-Domain Correlation Graph")
async def get_correlation_graph(
    incident_id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns an explainable multi-domain correlation graph linking endpoint,
    network, identity, threat intel, and Zero-Trust posture.
    """
    tenant_id = get_enforced_tenant_id(context)
    return await AutonomousCorrelationEngine.correlate_incident_context(
        db=db,
        tenant_id=tenant_id,
        incident_id=incident_id
    )
