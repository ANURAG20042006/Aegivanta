"""
tests/unit/test_phase26_correlation.py
======================================
Phase 26.4 Autonomous Multi-Domain Correlation Unit Tests.
"""

import pytest
from backend.app.services.advanced_incident_risk_service import AdvancedIncidentRiskEngine


class TestIncidentRiskScoring:
    """Unit tests for Multi-Factor Incident Risk Engine."""

    def test_critical_severity_gives_high_risk(self):
        """Critical severity and Tier 1 asset produces risk score >= 85."""
        res = AdvancedIncidentRiskEngine.calculate_incident_risk(
            severity="CRITICAL",
            asset_criticality="TIER_1_CRITICAL",
            identity_privilege="DOMAIN_ADMIN",
            ioc_confidence=0.95,
            lateral_hops=3,
            device_trust_score=20.0,
            ml_anomaly_score=0.95,
            attack_stage="EXFILTRATION"
        )
        assert res["risk_score"] >= 85.0
        assert res["risk_category"] == "CRITICAL"
        assert len(res["contributing_reasons"]) >= 3

    def test_low_severity_gives_low_risk(self):
        """Low severity and unprivileged user produces risk score < 40."""
        res = AdvancedIncidentRiskEngine.calculate_incident_risk(
            severity="LOW",
            asset_criticality="TIER_4_LOW",
            identity_privilege="USER",
            ioc_confidence=0.10,
            lateral_hops=0,
            device_trust_score=95.0,
            ml_anomaly_score=0.10,
            attack_stage="RECONNAISSANCE"
        )
        assert res["risk_score"] < 40.0
        assert res["risk_category"] == "LOW"

    def test_risk_score_within_zero_to_hundred(self):
        """Risk score must always stay strictly within [0.0, 100.0]."""
        res = AdvancedIncidentRiskEngine.calculate_incident_risk()
        assert 0.0 <= res["risk_score"] <= 100.0
