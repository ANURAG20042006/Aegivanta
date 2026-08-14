"""
backend/app/api/v1/predictive.py
================================
API Endpoints for Predictive Security Analytics, Asset Risk Forecasts & Volume Projections.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.core.dependencies import require_role
from backend.app.core.rate_limit import predictive_rate_limit
from backend.app.services.predictive_service import PredictiveService

router = APIRouter(prefix="/predictive", tags=["Predictive Security Analytics"])


@router.get("/assets/{asset_id}", summary="Get Asset Risk Forecast", dependencies=[Depends(predictive_rate_limit)])
async def get_asset_risk_forecast(
    asset_id: str,
    forecast_type: str = "24H",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Computes a 24H or 7D risk forecast for a specific protected asset."""
    try:
        forecast = await PredictiveService.compute_asset_forecast(asset_id, forecast_type, db)
        return {
            "id": forecast.id,
            "asset_id": forecast.asset_id,
            "forecast_type": forecast.forecast_type,
            "forecast_horizon": forecast.forecast_horizon,
            "predicted_score": forecast.predicted_score,
            "confidence": forecast.confidence,
            "baseline_score": forecast.baseline_score,
            "model_family": forecast.model_family,
            "model_version": forecast.model_version,
            "explanation": forecast.explanation,
            "created_at": forecast.created_at.isoformat() if forecast.created_at else None
        }
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.get("/volume", summary="Get Enterprise Alert Volume Forecast")
async def get_alert_volume_forecast(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Returns projected 24-hour enterprise alert volume based on recent telemetry velocity."""
    forecast = await PredictiveService.compute_volume_forecast(db)
    return {
        "id": forecast.id,
        "forecast_window": forecast.forecast_window,
        "predicted_alert_count": forecast.predicted_alert_count,
        "confidence": forecast.confidence,
        "model_family": forecast.model_family,
        "model_version": forecast.model_version,
        "historical_reference_count": forecast.historical_reference_count,
        "created_at": forecast.created_at.isoformat() if forecast.created_at else None
    }
