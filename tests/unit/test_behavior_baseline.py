"""
tests/unit/test_behavior_baseline.py
====================================
Phase 3.8 Unit Tests: Behavioral Baseline Engine.
"""

import pytest
from backend.app.services.behavior_baseline_service import BehaviorBaselineEngine


@pytest.mark.unit
def test_behavior_baseline_rolling_stats():
    """Verify mean and std calculation from observations."""
    obs = [10.0, 12.0, 9.0, 11.0, 10.5]
    stats = BehaviorBaselineEngine.compute_rolling_baseline(obs)
    assert stats["count"] == 5
    assert 10.0 <= stats["mean"] <= 11.0
    assert stats["std"] > 0.0


@pytest.mark.unit
def test_calculate_deviation_normal_and_anomaly():
    """Verify z-score calculation and explainable output."""
    # Normal behavior
    res_normal = BehaviorBaselineEngine.calculate_deviation(
        metric_name="packet_rate",
        observed_value=105.0,
        baseline_mean=100.0,
        baseline_std=10.0
    )
    assert res_normal["is_anomalous"] is False
    assert res_normal["severity"] == "LOW"
    assert "within normal" in res_normal["explanation"]

    # Critical Anomaly (z = 4.5)
    res_anom = BehaviorBaselineEngine.calculate_deviation(
        metric_name="packet_rate",
        observed_value=145.0,
        baseline_mean=100.0,
        baseline_std=10.0
    )
    assert res_anom["is_anomalous"] is True
    assert res_anom["severity"] == "CRITICAL"
    assert res_anom["anomaly_score"] >= 75.0
    assert "deviates by +4.50" in res_anom["explanation"]
