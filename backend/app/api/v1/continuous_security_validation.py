"""
backend/app/api/v1/continuous_security_validation.py
====================================================
Phase 26.1 Continuous Security Validation API Endpoints.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.continuous_security_validation_service import ContinuousSecurityValidationService

router = APIRouter(prefix="/security/continuous-validation", tags=["Continuous Security Validation"])


@router.get("", summary="Get Latest Continuous Security Validation Report")
async def get_latest_validation(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves the latest continuous defense verification report."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ContinuousSecurityValidationService.get_latest_validation_summary(db, tenant_id)


@router.post("/run", summary="Trigger On-Demand Continuous Security Validation")
async def trigger_validation_run(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Executes on-demand continuous security defense validation across all 16 domains."""
    tenant_id = context.tenant_id or "default-tenant"
    run = await ContinuousSecurityValidationService.run_validation(db, tenant_id, trigger_type="ON_DEMAND")
    return await ContinuousSecurityValidationService.get_latest_validation_summary(db, tenant_id)


@router.get("/history", summary="Get Historical Continuous Validation Runs")
async def get_validation_history(
    limit: int = Query(15, ge=1, le=50),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves historical validation runs for trend analysis."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ContinuousSecurityValidationService.get_validation_history(db, tenant_id, limit)
