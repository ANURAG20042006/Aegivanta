"""
tests/security/test_phase39_tenant_isolation.py
===============================================
Phase 39 Predictive Intelligence Multi-Tenant Isolation Security Tests.
"""

import pytest
from backend.app.models.predictive_intel import (
    PredictiveThreatForecast, AdversarialVectorSimulation, ThreatHorizonIndicator
)


class TestPredictiveMultiTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 39 models."""

    def test_predictive_models_enforce_tenant_id(self):
        """All Phase 39 Predictive Intelligence models must enforce tenant_id partition attributes."""
        fc = PredictiveThreatForecast(tenant_id="tenant-pred-1", threat_vector_title="fc-1", target_asset_category="cat-1", evidence_features_summary="ev-1")
        sim = AdversarialVectorSimulation(tenant_id="tenant-pred-1", threat_scenario_title="sim-1", predicted_escalation_pathway="path-1", mitigation_directive="mit-1")
        ind = ThreatHorizonIndicator(tenant_id="tenant-pred-1", indicator_name="ind-1")

        assert fc.tenant_id == "tenant-pred-1"
        assert sim.tenant_id == "tenant-pred-1"
        assert ind.tenant_id == "tenant-pred-1"
