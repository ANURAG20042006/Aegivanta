"""
tests/unit/test_response_decisions.py
=====================================
Phase 3.7 Unit Tests: Response Decision Engine.
Verifies multi-signal threat evaluation, recommended action selection, and explainability.
"""

import pytest
from backend.app.services.response_decision_service import ResponseDecisionService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_decision_lateral_movement_recommends_isolate_host():
    """Verify lateral movement or blast radius triggers ISOLATE_HOST recommendation."""
    decision = await ResponseDecisionService.evaluate_incident_response(
        incident_id="inc-test-01",
        risk_score=85.0,
        severity="HIGH",
        attack_type="Lateral Movement",
        has_lateral_movement=True,
        blast_radius_score=65.0,
        source_ip="10.0.0.50"
    )
    assert decision["is_allowed"] is True
    assert decision["primary_recommended_action"] == "ISOLATE_HOST"
    assert "Lateral movement" in decision["reason"]
    assert decision["requires_approval"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_decision_ioc_match_recommends_block_ip():
    """Verify threat intel IOC match triggers BLOCK_IP recommendation."""
    decision = await ResponseDecisionService.evaluate_incident_response(
        incident_id="inc-test-02",
        risk_score=75.0,
        severity="HIGH",
        attack_type="C2 Beaconing",
        matched_iocs_count=2,
        source_ip="198.51.100.25"
    )
    assert decision["is_allowed"] is True
    assert decision["primary_recommended_action"] == "BLOCK_IP"
    assert "Active threat indicator" in decision["reason"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_decision_credential_abuse_recommends_session_revocation():
    """Verify Kerberos/Credential attack triggers REVOKE_SESSION and DISABLE_ACCOUNT."""
    decision = await ResponseDecisionService.evaluate_incident_response(
        incident_id="inc-test-03",
        risk_score=80.0,
        severity="HIGH",
        attack_type="Kerberoasting",
        source_ip="10.0.0.22"
    )
    assert "REVOKE_SESSION" in decision["all_recommended_actions"]
    assert "DISABLE_ACCOUNT" in decision["all_recommended_actions"]
    assert "Credential manipulation" in decision["reason"]
