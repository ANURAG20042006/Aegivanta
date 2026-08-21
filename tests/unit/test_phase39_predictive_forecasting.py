"""
tests/unit/test_phase39_predictive_forecasting.py
=================================================
Phase 39 Predictive Forecasting Unit Tests.
"""

import pytest
from backend.app.models.predictive_intel import PredictiveThreatForecast


class TestPredictiveForecasting:
    """Unit tests for PredictiveThreatForecast model."""

    def test_predictive_forecast_model_creation(self):
        """PredictiveThreatForecast must store vector title, asset category, probability, and horizon."""
        fc = PredictiveThreatForecast(
            tenant_id="tenant-pred",
            threat_vector_title="Supply Chain Typosquatting",
            target_asset_category="CI/CD Runners",
            probability_score=0.88,
            predicted_impact_severity="CRITICAL",
            forecast_horizon="30_DAYS",
            confidence_score=0.94,
            evidence_features_summary="Upstream registry telemetry indicated malicious package ingestion.",
            model_version="v39.1.0-forecaster"
        )
        assert fc.threat_vector_title == "Supply Chain Typosquatting"
        assert fc.probability_score == 0.88
        assert fc.predicted_impact_severity == "CRITICAL"
        assert fc.forecast_horizon == "30_DAYS"
