import pytest
from backend.app.services.soar_orchestrator_v2 import SOAROrchestratorV2


def test_autonomous_decision_for_critical_asset():
    # Critical assets must require human approval regardless of high confidence
    res = SOAROrchestratorV2.evaluate_autonomous_decision(
        severity="CRITICAL",
        confidence=0.98,
        threat_score=95.0,
        asset_criticality="CRITICAL",
        kill_chain_stage="EXPLOITATION"
    )

    assert res["requires_human_approval"] is True
    assert res["recommended_decision"] == "HOLD_FOR_APPROVAL"
    assert "Criticality" in res["explanation"]


def test_autonomous_decision_for_non_critical_asset_high_confidence():
    # Non-critical assets with high confidence execute autonomously
    res = SOAROrchestratorV2.evaluate_autonomous_decision(
        severity="HIGH",
        confidence=0.95,
        threat_score=85.0,
        asset_criticality="LOW",
        kill_chain_stage="DELIVERY"
    )

    assert res["requires_human_approval"] is False
    assert res["recommended_decision"] == "AUTONOMOUS_CONTAINMENT"
    assert res["total_risk_score"] >= 60.0

