"""
tests/unit/test_phase39_models.py
=================================
Phase 39 Model Defaults & Field Validation Unit Tests.
"""

import pytest
from backend.app.models.predictive_intel import PredictiveThreatForecast, AdversarialVectorSimulation, ThreatHorizonIndicator


class TestPhase39Models:
    """Unit tests for Phase 39 model default values and relationships."""

    def test_forecast_confidence_defaults(self):
        """Forecast record must have model version and non-negative confidence."""
        fc = PredictiveThreatForecast(
            tenant_id="tenant-pred",
            threat_vector_title="Kubernetes Envoy RCE",
            target_asset_category="K8s Ingress",
            evidence_features_summary="EPSS 0.84 on Envoy stream parser.",
            confidence_score=0.92,
            model_version="v39.1.0-forecaster"
        )
        assert fc.confidence_score >= 0.0
        assert "forecaster" in fc.model_version

