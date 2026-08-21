"""
backend/app/api/v1/global_ops.py
==================================
Phase 24 Global Operations, FinOps, Capacity, and SRE API Router.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.services.finops_capacity_service import FinOpsCapacityService
from backend.app.observability import metrics

router = APIRouter(prefix="/global-ops", tags=["Phase 24 - Global Operations & FinOps"])


@router.get("/finops/dashboard")
async def get_finops_dashboard(
    tenant_id: str = "default-tenant"
):
    """Returns tenant-aware FinOps cost breakdown and monthly trends."""
    return FinOpsCapacityService.get_finops_dashboard(tenant_id=tenant_id)


@router.get("/capacity/dashboard")
async def get_capacity_dashboard(
    tenant_id: str = "default-tenant"
):
    """Returns real-time capacity planning metrics: EPS, CPU, memory, queue depth."""
    return FinOpsCapacityService.get_capacity_dashboard(tenant_id=tenant_id)


@router.get("/sre/slo-dashboard")
async def get_slo_dashboard():
    """Returns SLO compliance, error budget consumption, and reliability metrics."""
    return FinOpsCapacityService.get_slo_dashboard()
