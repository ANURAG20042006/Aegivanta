"""
tests/security/test_phase26_remediation.py
==========================================
Phase 26 Automated Remediation Governance Security Tests.
"""

import pytest
from backend.app.services.remediation_governance_service import (
    RemediationGovernanceService, ACTION_RISK_MATRIX
)


class TestRemediationGovernanceSecurity:
    """Security tests for remediation action risk classification and approval gates."""

    def test_critical_actions_always_require_approval(self):
        """CRITICAL actions must strictly require approval regardless of settings."""
        for act, meta in ACTION_RISK_MATRIX.items():
            if meta["risk_level"] == "CRITICAL":
                eval_res = RemediationGovernanceService.evaluate_action_policy(act, user_role="ADMIN", auto_remediation_enabled=True)
                assert eval_res["requires_approval"] is True

    def test_low_risk_actions_can_auto_execute(self):
        """LOW risk actions can auto-execute without blocking for approval."""
        eval_res = RemediationGovernanceService.evaluate_action_policy("ADD_TAG", user_role="SECURITY_ANALYST")
        assert eval_res["requires_approval"] is False
        assert eval_res["policy_decision"] == "AUTO_EXECUTE_PERMITTED"
