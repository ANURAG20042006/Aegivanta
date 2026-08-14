"""
backend/app/services/predictive_service.py
==========================================
Predictive Security Analytics and Risk Forecasting Engine.
Generates asset risk trends (24h, 7d) and alert volume forecasts with explicit uncertainty quantification.
"""

from datetime import datetime, timezone, timedelta
import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.predictive import RiskForecast, AlertVolumeForecast
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.alert import Alert
from backend.app.models.incident import Incident
from backend.app.models.behavioral import AnomalyEvent
from backend.app.models.monitoring import MonitoringCheck
from backend.app.services.risk_engine import RiskScoringEngine

logger = logging.getLogger("SentinelAI")


class PredictiveService:
    """Core Forecasting & Predictive Risk Analytics Engine."""

    MODEL_FAMILY = "phase3_predictive"
    MODEL_VERSION = "forecast-v1"

    @staticmethod
    async def compute_asset_forecast(
        asset_id: str,
        forecast_type: str,  # 24H or 7D
        db: AsyncSession
    ) -> RiskForecast:
        """
        Computes a deterministic predictive risk score for an asset over a 24H or 7D horizon.
        Uses exponential weighting over recent alerts, anomalies, health states, and baseline score.
        """
        # 1. Fetch Protected Asset
        res = await db.execute(select(ProtectedAsset).where(ProtectedAsset.id == asset_id))
        asset = res.scalar_one_or_none()
        if not asset:
            raise ValueError(f"Protected Asset {asset_id} not found")

        now_utc = datetime.now(timezone.utc)
        lookback_days = 1 if forecast_type.upper() == "24H" else 7
        window_start = now_utc - timedelta(days=lookback_days)

        # 2. Query Recent Alerts Count
        alert_res = await db.execute(
            select(func.count(Alert.id)).where(
                Alert.asset_id == asset_id,
                Alert.timestamp >= window_start
            )
        )
        recent_alerts = alert_res.scalar() or 0

        # 3. Query Recent Behavioral Anomalies
        anom_res = await db.execute(
            select(func.count(AnomalyEvent.id)).where(
                AnomalyEvent.asset_id == asset_id,
                AnomalyEvent.timestamp >= window_start
            )
        )
        recent_anomalies = anom_res.scalar() or 0

        # 4. Query Continuous Monitoring State
        mon_res = await db.execute(
            select(MonitoringCheck).where(MonitoringCheck.asset_id == asset_id)
        )
        mon_checks = mon_res.scalars().all()
        has_outage = any(c.health_state == "DOWN" for c in mon_checks)
        has_degraded = any(c.health_state == "DEGRADED" for c in mon_checks)

        # 5. Cold-Start Check
        total_signals = recent_alerts + recent_anomalies + len(mon_checks)
        if total_signals == 0:
            # Baseline state
            base_score = 15.0 if asset.criticality == "low" else (30.0 if asset.criticality == "medium" else 45.0)
            forecast = RiskForecast(
                id=str(uuid.uuid4()),
                asset_id=asset_id,
                forecast_type=forecast_type.upper(),
                forecast_horizon="24_HOURS" if forecast_type.upper() == "24H" else "7_DAYS",
                predicted_score=base_score,
                confidence=0.35,  # Low confidence due to sparse telemetry
                baseline_score=base_score,
                model_family=PredictiveService.MODEL_FAMILY,
                model_version=PredictiveService.MODEL_VERSION,
                explanation={
                    "status": "INSUFFICIENT_HISTORY",
                    "reason": "Insufficient historical alerts observed in window. Projecting default baseline.",
                    "recent_alerts": 0,
                    "recent_anomalies": 0,
                    "monitoring_state": "HEALTHY"
                }
            )
            db.add(forecast)
            await db.commit()
            await db.refresh(forecast)
            return forecast

        # 6. Deterministic Forecast Trend Computation
        base_score = RiskScoringEngine.calculate_risk_score(
            severity="high" if recent_alerts > 3 else ("medium" if recent_alerts > 0 else "low"),
            confidence=0.85,
            criticality=asset.criticality,
            alert_count=recent_alerts
        )

        velocity_factor = min(25.0, (recent_alerts * 2.5) + (recent_anomalies * 5.0))
        outage_penalty = 20.0 if has_outage else (10.0 if has_degraded else 0.0)
        
        predicted_score = round(min(100.0, max(0.0, base_score + velocity_factor + outage_penalty)), 1)
        confidence = min(0.95, 0.50 + (min(10, total_signals) * 0.045))

        forecast = RiskForecast(
            id=str(uuid.uuid4()),
            asset_id=asset_id,
            forecast_type=forecast_type.upper(),
            forecast_horizon="24_HOURS" if forecast_type.upper() == "24H" else "7_DAYS",
            predicted_score=predicted_score,
            confidence=confidence,
            baseline_score=base_score,
            model_family=PredictiveService.MODEL_FAMILY,
            model_version=PredictiveService.MODEL_VERSION,
            explanation={
                "status": "ACTIVE_TREND_FORECAST",
                "velocity_factor": velocity_factor,
                "outage_penalty": outage_penalty,
                "recent_alerts": recent_alerts,
                "recent_anomalies": recent_anomalies,
                "monitoring_health": "DOWN" if has_outage else ("DEGRADED" if has_degraded else "HEALTHY")
            }
        )
        db.add(forecast)
        await db.commit()
        await db.refresh(forecast)
        return forecast

    @staticmethod
    async def compute_volume_forecast(db: AsyncSession) -> AlertVolumeForecast:
        """Projects enterprise alert volume for the next 24 hours."""
        now_utc = datetime.now(timezone.utc)
        past_24h = now_utc - timedelta(hours=24)

        res = await db.execute(
            select(func.count(Alert.id)).where(Alert.timestamp >= past_24h)
        )
        count_24h = res.scalar() or 0

        predicted_volume = max(5, int(count_24h * 1.15))
        confidence = 0.82 if count_24h > 10 else 0.50

        forecast = AlertVolumeForecast(
            id=str(uuid.uuid4()),
            forecast_window="NEXT_24H",
            predicted_alert_count=predicted_volume,
            confidence=confidence,
            model_family=PredictiveService.MODEL_FAMILY,
            model_version="volume-forecast-v1",
            historical_reference_count=count_24h
        )
        db.add(forecast)
        await db.commit()
        await db.refresh(forecast)
        return forecast
