"""
backend/app/api/v1/predictive_intel.py
======================================
Phase 39 Predictive Security Intelligence & Emerging Threat Forecasting API Router.
Exposes:
- Predictive Intelligence Posture Scorecard
- 30/60/90-Day Emerging Threat Vector Forecasts
- Generate Custom Threat Forecast
- Adversarial Attack Vector Simulations & Blast Radius
- Global Threat Horizon Indicators & Surge Trends
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.predictive_forecasting_service import PredictiveForecastingService
from backend.app.services.adversarial_simulation_service import AdversarialSimulationService
from backend.app.services.predictive_posture_service import PredictivePostureService

router = APIRouter(prefix="/predictive-intel", tags=["Phase 39 - Predictive Security Intelligence"])


# ==================== Request Payloads ====================

class GenerateForecastRequest(BaseModel):
    threat_vector_title: str = Field(..., example="Supply Chain PyPI Poisoning")
    target_asset_category: str = Field(..., example="CI/CD Deployment Runners")
    forecast_horizon: str = Field(default="30_DAYS", example="30_DAYS")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get Predictive Security Intelligence Scorecard")
async def get_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates consolidated predictive intelligence score and metrics."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PredictivePostureService.get_summary(db=db, tenant_id=tenant_id)


# Forecasts
@router.get("/forecasts", summary="List Emerging Threat Vector Forecasts")
async def list_forecasts(
    horizon: Optional[str] = Query(None, example="30_DAYS"),
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists predictive threat forecasts."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PredictiveForecastingService.list_forecasts(
        db=db,
        tenant_id=tenant_id,
        horizon=horizon,
        limit=limit
    )


@router.post("/forecasts/generate", summary="Generate Predictive Threat Forecast")
async def generate_forecast(
    req: GenerateForecastRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Generates a new predictive threat forecast using ML ensemble models."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PredictiveForecastingService.generate_forecast(
        db=db,
        tenant_id=tenant_id,
        threat_vector_title=req.threat_vector_title,
        target_asset_category=req.target_asset_category,
        forecast_horizon=req.forecast_horizon
    )


# Simulations
@router.get("/simulations", summary="List Adversarial Vector Simulations")
async def list_simulations(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists adversarial attack simulations."""
    tenant_id = context.tenant_id or "default-tenant"
    return await AdversarialSimulationService.list_simulations(db=db, tenant_id=tenant_id, limit=limit)


# Horizon Indicators
@router.get("/horizon-indicators", summary="List Global Threat Horizon Trends")
async def list_horizon_indicators(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists global threat horizon trends."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PredictiveForecastingService.list_horizon_indicators(db=db, tenant_id=tenant_id, limit=limit)
