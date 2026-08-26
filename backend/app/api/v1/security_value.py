from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext, get_enforced_tenant_id
from backend.app.services.security_value_service import SecurityValueService
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="", tags=["Security Value, Cost Intelligence & Posture"])


@router.get("/analytics/security-value", summary="Get Customer Cybersecurity ROI & Value Metrics")
async def get_security_value(
    lookback_days: int = Query(30, ge=1, le=365),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates threats blocked, MTTD/MTTA/MTTR, risk reduction %, and historical trend series."""
    tenant_id = get_enforced_tenant_id(context)
    return await SecurityValueService.get_security_value_metrics(db, tenant_id, lookback_days)


@router.get("/security-posture/improvements", summary="Get Explainable Security Posture Improvements")
async def get_posture_improvements(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Returns prioritized security actions with estimated impact scores."""
    tenant_id = get_enforced_tenant_id(context)
    return await SecurityValueService.get_posture_improvements(db, tenant_id)


@router.get("/telemetry/cost-intelligence", summary="Get Telemetry Cost Intelligence & Optimization")
async def get_telemetry_cost_intelligence(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Analyzes telemetry volume, duplicate trends, and actionable storage savings."""
    tenant_id = get_enforced_tenant_id(context)
    return await SecurityValueService.get_telemetry_cost_intelligence(db, tenant_id)


@router.get("/analytics/product", summary="Get Privacy-Conscious Product Operations Analytics")
async def get_product_analytics(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Platform-level operational metric rollups for administrative monitoring."""
    return await SecurityValueService.get_product_analytics(db)
