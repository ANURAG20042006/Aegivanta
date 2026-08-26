from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext, get_enforced_tenant_id
from backend.app.services.security_intelligence_service import SecurityIntelligenceService

router = APIRouter(prefix="", tags=["Security Intelligence & Coverage"])


@router.get("/detection/coverage/gaps", summary="Get MITRE ATT&CK Detection Coverage Gaps")
async def get_coverage_gaps(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Identifies techniques without detection rules and provides recommended telemetry."""
    tenant_id = get_enforced_tenant_id(context)
    return await SecurityIntelligenceService.get_coverage_gaps(db, tenant_id)


@router.get("/security/attack-paths", summary="Get Attack Path Risk Graph")
async def get_attack_paths(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates multi-hop attack path risk graph, blast radius, and containment cut-points."""
    tenant_id = get_enforced_tenant_id(context)
    return await SecurityIntelligenceService.get_attack_paths(db, tenant_id)


@router.get("/assets/risk", summary="Get Dynamic Protected Asset Risk Intelligence")
async def get_asset_risk_scores(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Computes dynamic 0–100 risk score and explainable factor breakdown for protected assets."""
    tenant_id = get_enforced_tenant_id(context)
    return await SecurityIntelligenceService.get_asset_risk_scores(db, tenant_id)


@router.get("/security/control-effectiveness", summary="Get Security Control Effectiveness")
async def get_control_effectiveness(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Measures empirical threat mitigation performance of active security controls."""
    tenant_id = get_enforced_tenant_id(context)
    return await SecurityIntelligenceService.get_control_effectiveness(db, tenant_id)
