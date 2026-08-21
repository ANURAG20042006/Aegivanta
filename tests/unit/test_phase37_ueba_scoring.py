"""
tests/unit/test_phase37_ueba_scoring.py
=======================================
Phase 37 UEBA Scoring Unit Tests.
"""

import pytest
from backend.app.services.ueba_scoring_service import UEBAScoringService


class TestUEBAScoring:
    """Unit tests for dynamic User Risk Score (URS) computation."""

    def test_urs_calculation_baseline(self):
        """Normal user with no anomalies must receive LOW risk level."""
        res = UEBAScoringService.calculate_user_risk_score(
            anomalies=[],
            daily_egress_mb=200.0,
            baseline_egress_mb=400.0,
            is_odd_hours=False,
            is_velocity_anomalous=False
        )
        assert res["user_risk_score"] <= 35
        assert res["risk_level"] == "LOW"

    def test_urs_calculation_critical_anomaly(self):
        """Mass egress, odd hours, and anomalous velocity must produce CRITICAL risk level."""
        res = UEBAScoringService.calculate_user_risk_score(
            anomalies=["MASS_EXPORT", "TOR_ACCESS"],
            daily_egress_mb=3500.0,
            baseline_egress_mb=400.0,
            is_odd_hours=True,
            is_velocity_anomalous=True
        )
        assert res["user_risk_score"] >= 80
        assert res["risk_level"] == "CRITICAL"
