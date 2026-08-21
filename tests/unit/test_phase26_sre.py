"""
tests/unit/test_phase26_sre.py
==============================
Phase 26.12 & 26.13 SRE, SLO, and Chaos Engineering Unit Tests.
"""

import pytest
from backend.app.services.sre_slo_validation_service import SRESLOValidationService
from backend.app.services.security_chaos_service import SecurityChaosService, CHAOS_SCENARIOS


class TestSREValidationAndChaos:
    """Unit tests for SRE health, SLO compliance, and chaos engineering."""

    def test_sre_health_returns_all_components(self):
        """Platform SRE health report must include all primary architectural components."""
        health = SRESLOValidationService.get_platform_sre_health()
        assert health["status"] == "HEALTHY"
        comps = health["components"]
        assert "api_gateway" in comps
        assert "redis_streams" in comps
        assert "postgresql_cluster" in comps
        assert "ml_inference_workers" in comps
        assert "sensor_fleet" in comps
        assert "webhook_platform" in comps

    def test_slo_metrics_all_compliant(self):
        """Standard SLO performance checks must be verified."""
        slo_report = SRESLOValidationService.get_slo_metrics()
        assert slo_report["overall_compliance"] is True
        assert len(slo_report["slos"]) >= 5

    def test_error_budget_analytics(self):
        """Error budget remaining percent must be positive and burn rate nominal."""
        budget = SRESLOValidationService.get_error_budget_analytics()
        assert budget["remaining_budget_pct"] > 0.0
        assert budget["current_burn_rate"] < 1.0

    def test_chaos_scenarios_populated(self):
        """Chaos scenarios must contain at least 8 defined failure modes."""
        assert len(CHAOS_SCENARIOS) >= 8

    def test_run_chaos_simulation_verifies_graceful_degradation(self):
        """Executing chaos simulation must return graceful degradation verified."""
        result = SecurityChaosService.run_chaos_simulation("REDIS_OUTAGE")
        assert result["status"] == "PASSED"
        assert result["graceful_degradation_verified"] is True
        assert result["data_loss_occurred"] is False
