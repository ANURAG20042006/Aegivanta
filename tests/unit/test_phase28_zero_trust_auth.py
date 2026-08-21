"""
tests/unit/test_phase28_zero_trust_auth.py
==========================================
Phase 28 Zero Trust Continuous Adaptive Authorization Unit Tests.
"""

import pytest
from backend.app.services.zero_trust_continuous_auth_service import ZeroTrustContinuousAuthService


class TestZeroTrustContinuousAuth:
    """Unit tests for continuous authorization policy evaluation."""

    def test_low_risk_managed_device_returns_allow(self):
        """Low risk session from managed device with known location returns ALLOW."""
        res = ZeroTrustContinuousAuthService.evaluate_session_access(
            username="sarah.connor@aegivanta.io",
            identity_risk_score=10.0,
            device_trust_score=95.0,
            resource_criticality="MEDIUM",
            is_known_location=True,
            is_managed_device=True
        )
        assert res["verdict"] == "ALLOW"
        assert res["composite_session_risk"] < 35.0

    def test_high_risk_session_terminates_access(self):
        """High risk session (>80.0) returns TERMINATE_SESSION verdict."""
        res = ZeroTrustContinuousAuthService.evaluate_session_access(
            username="attacker@aegivanta.io",
            identity_risk_score=90.0,
            device_trust_score=20.0,
            resource_criticality="CRITICAL",
            is_known_location=False,
            is_managed_device=False
        )
        assert res["verdict"] == "TERMINATE_SESSION"
        assert res["action_code"] == "REVOKE_JWT_IMMEDIATE"
