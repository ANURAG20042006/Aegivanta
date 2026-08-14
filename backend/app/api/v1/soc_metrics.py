"""
backend/app/api/v1/soc_metrics.py
=================================
API Endpoints for SOC Effectiveness Metrics (MTTD, MTTR, Workload, Ratios).
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.core.dependencies import require_role
from backend.app.services.soc_metrics_service import SOCMetricsService

router = APIRouter(prefix="/soc-metrics", tags=["SOC Effectiveness Analytics"])


@router.get("/overview", summary="Get SOC Effectiveness Overview KPIs")
async def get_soc_overview(
    lookback_days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Calculates MTTD, MTTR, Alert-to-Incident compression, and false positive metrics."""
    return await SOCMetricsService.get_soc_overview(lookback_days=lookback_days, db=db)


@router.get("/workload", summary="Get Analyst Workload Distribution")
async def get_analyst_workload(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Returns analyst investigation and playbook action workload distributions."""
    return await SOCMetricsService.get_analyst_workload(db=db)
