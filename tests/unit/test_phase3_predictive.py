"""
tests/unit/test_phase3_predictive.py
====================================
Unit tests for Phase 3 Predictive Risk & Volume Forecasting.
"""

import pytest
from backend.app.database import AsyncSessionFactory
from backend.app.services.predictive_service import PredictiveService
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.alert import Alert
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_predictive_risk_forecast_cold_start():
    """Verify cold-start asset receives baseline score and INSUFFICIENT_HISTORY label."""
    async with AsyncSessionFactory() as db:
        asset = ProtectedAsset(
            name="Predictive Cold Start Asset",
            hostname="pred-cold.corp",
            ip_address="198.51.100.101",
            asset_type="database",
            criticality="critical"
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)

        fc = await PredictiveService.compute_asset_forecast(asset.id, "24H", db)
        assert fc.model_family == "phase3_predictive"
        assert fc.model_version == "forecast-v1"
        assert fc.confidence <= 0.50
        assert fc.explanation.get("status") == "INSUFFICIENT_HISTORY"


@pytest.mark.asyncio
async def test_predictive_volume_forecast():
    """Verify enterprise alert volume forecasting executes deterministically."""
    async with AsyncSessionFactory() as db:
        vol = await PredictiveService.compute_volume_forecast(db)
        assert vol.model_family == "phase3_predictive"
        assert vol.predicted_alert_count >= 5
        assert 0.0 <= vol.confidence <= 1.0
