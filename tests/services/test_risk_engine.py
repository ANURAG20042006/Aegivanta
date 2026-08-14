import pytest
from backend.app.services.risk_engine import RiskScoringEngine, SEVERITY_WEIGHTS, CRITICALITY_WEIGHTS


def test_risk_score_calculation_critical_threat():
    """Test critical severity + high confidence on critical asset computes max risk."""
    score = RiskScoringEngine.calculate_risk_score(
        severity="CRITICAL",
        confidence=1.0,
        criticality="critical",
        alert_count=10
    )
    # (1.0*40) + (1.0*25) + (1.0*20) + (1.0*15) = 100.0
    assert score == 100.0
    assert RiskScoringEngine.get_risk_tier(score) == "CRITICAL"


def test_risk_score_calculation_low_threat():
    """Test low severity + low confidence on low criticality asset with single alert."""
    score = RiskScoringEngine.calculate_risk_score(
        severity="LOW",
        confidence=0.2,
        criticality="low",
        alert_count=1
    )
    # (0.25*40) + (0.2*25) + (0.25*20) + (0.1*15) = 10 + 5 + 5 + 1.5 = 21.5
    assert score == 21.5
    assert RiskScoringEngine.get_risk_tier(score) == "LOW"


def test_risk_score_confidence_fallback():
    """Test risk engine defaults confidence to 0.5 if unavailable."""
    score = RiskScoringEngine.calculate_risk_score(
        severity="HIGH",
        confidence=None,
        criticality="medium",
        alert_count=1
    )
    # (0.75*40) + (0.5*25) + (0.50*20) + (0.1*15) = 30 + 12.5 + 10 + 1.5 = 54.0
    assert score == 54.0
    assert RiskScoringEngine.get_risk_tier(score) == "HIGH"


def test_risk_recurrence_saturation():
    """Test recurrence factor saturates at 10 alerts."""
    score_10 = RiskScoringEngine.calculate_risk_score("HIGH", 0.8, "high", 10)
    score_50 = RiskScoringEngine.calculate_risk_score("HIGH", 0.8, "high", 50)
    assert score_10 == score_50


def test_risk_score_breakdown_transparency():
    """Test score breakdown structure and mathematical components."""
    breakdown = RiskScoringEngine.get_score_breakdown(
        severity="MEDIUM",
        confidence=0.9,
        criticality="high",
        alert_count=4
    )
    assert "risk_score" in breakdown
    assert "tier" in breakdown
    assert "components" in breakdown
    comps = breakdown["components"]
    assert "severity_contribution" in comps
    assert "confidence_contribution" in comps
    assert "criticality_contribution" in comps
    assert "recurrence_contribution" in comps
    
    total_components = (
        comps["severity_contribution"] +
        comps["confidence_contribution"] +
        comps["criticality_contribution"] +
        comps["recurrence_contribution"]
    )
    assert abs(breakdown["risk_score"] - round(total_components, 1)) < 0.2
