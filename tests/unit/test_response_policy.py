"""
tests/unit/test_response_policy.py
==================================
Phase 3.7 Unit Tests: Centralized Response Policy Engine.
Verifies risk tiers (LOW, MEDIUM, HIGH, CRITICAL), policy decisions, action filtering,
and approval requirements.
"""

import pytest
from backend.app.services.response_policy_service import ResponsePolicyEngine


@pytest.mark.unit
@pytest.mark.asyncio
async def test_policy_tier_low_no_automation():
    """Verify LOW severity / risk score prohibits automated response."""
    eval_res = await ResponsePolicyEngine.evaluate(
        risk_score=15.0,
        severity="LOW",
        requested_action="BLOCK_IP"
    )
    assert eval_res["is_allowed"] is False
    assert eval_res["decision"] == "DENY_NO_AUTOMATION"
    assert "prohibits automation" in eval_res["reason"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_policy_tier_medium_alert_only():
    """Verify MEDIUM severity allows notification actions but denies destructive actions."""
    # Allowed non-destructive action
    eval_ok = await ResponsePolicyEngine.evaluate(
        risk_score=35.0,
        severity="MEDIUM",
        requested_action="NOTIFY_ANALYST"
    )
    assert eval_ok["is_allowed"] is True
    assert eval_ok["decision"] == "ALLOW"
    assert eval_ok["requires_approval"] is False

    # Denied destructive action
    eval_deny = await ResponsePolicyEngine.evaluate(
        risk_score=35.0,
        severity="MEDIUM",
        requested_action="BLOCK_IP"
    )
    assert eval_deny["is_allowed"] is False
    assert eval_deny["decision"] == "DENY_ACTION_UNSUPPORTED"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_policy_tier_high_requires_approval():
    """Verify HIGH severity requires mandatory two-tier approval for containment actions."""
    eval_res = await ResponsePolicyEngine.evaluate(
        risk_score=65.0,
        severity="HIGH",
        requested_action="ISOLATE_HOST"
    )
    assert eval_res["is_allowed"] is True
    assert eval_res["requires_approval"] is True
    assert eval_res["decision"] == "REQUIRE_APPROVAL"
    assert "ISOLATE_HOST" in eval_res["allowed_actions"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_policy_tier_critical_evaluation():
    """Verify CRITICAL severity allows full suite of containment actions."""
    eval_res = await ResponsePolicyEngine.evaluate(
        risk_score=90.0,
        severity="CRITICAL",
        requested_action="DISABLE_ACCOUNT"
    )
    assert eval_res["is_allowed"] is True
    assert "DISABLE_ACCOUNT" in eval_res["allowed_actions"]
    assert "BLOCK_IP" in eval_res["allowed_actions"]
    assert "ISOLATE_HOST" in eval_res["allowed_actions"]
