"""
tests/unit/test_risk_scoring.py
===============================
Phase 3.6 Unit Tests: Deterministic Risk-Based Alert & Incident Prioritization.
Verifies multi-dimensional scoring formula, 0-100 normalization, and component explainability.
"""

import pytest
from backend.app.services.risk_scoring_service import RiskScoringService


@pytest.mark.unit
def test_risk_score_bands_classification():
    """Verify classification thresholds."""
    assert RiskScoringService.classify_score_band(10.0) == "LOW"
    assert RiskScoringService.classify_score_band(25.0) == "MEDIUM"
    assert RiskScoringService.classify_score_band(55.0) == "HIGH"
    assert RiskScoringService.classify_score_band(85.0) == "CRITICAL"


@pytest.mark.unit
def test_risk_score_benign_event():
    """Verify minimal score for low-severity benign events."""
    score, band, comps = RiskScoringService.calculate_incident_risk(
        severity="LOW",
        confidence=0.50,
        ioc_match_count=0,
        asset_criticality="LOW",
        event_count=1
    )
    assert score <= 25.0
    assert band in ["LOW", "MEDIUM"]
    assert comps["total_normalized_score"] == score
    assert "base_severity_contribution" in comps


@pytest.mark.unit
def test_risk_score_critical_multi_signal_attack():
    """Verify high/critical score for multi-signal attack with IOC, lateral movement, and critical asset."""
    score, band, comps = RiskScoringService.calculate_incident_risk(
        severity="CRITICAL",
        confidence=0.95,
        ioc_match_count=2,
        max_ioc_confidence=0.90,
        asset_criticality="CRITICAL",
        affected_asset_count=3,
        event_count=15,
        hop_count=3,
        has_lateral_movement=True,
        crown_jewel_index=80.0,
        blast_radius_score=60.0
    )
    assert score >= 75.0
    assert band == "CRITICAL"
    assert comps["threat_intel_contribution"] > 0
    assert comps["lateral_movement_contribution"] > 0
    assert comps["blast_radius_contribution"] > 0


@pytest.mark.unit
def test_risk_score_clamping():
    """Verify risk scores never exceed 100.0 or go below 0.0."""
    max_score, _, _ = RiskScoringService.calculate_incident_risk(
        severity="CRITICAL",
        confidence=1.0,
        ioc_match_count=100,
        max_ioc_confidence=1.0,
        asset_criticality="CRITICAL",
        affected_asset_count=50,
        event_count=1000,
        hop_count=10,
        has_lateral_movement=True,
        crown_jewel_index=100.0,
        blast_radius_score=100.0,
        velocity_events_per_minute=500.0
    )
    assert max_score == 100.0

    min_score, _, _ = RiskScoringService.calculate_incident_risk(
        severity="INFORMATIONAL",
        confidence=0.1,
        asset_criticality="LOW",
        event_count=1
    )
    assert 0.0 <= min_score <= 15.0
