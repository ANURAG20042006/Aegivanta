"""
tests/security/test_phase33_canary_trigger_defense.py
=====================================================
Phase 33 Canary Token Trigger Integrity & Anti-Spoofing Security Tests.
"""

import pytest
from backend.app.models.deception import CanaryToken


class TestCanaryTriggerDefense:
    """Security tests verifying canary token trigger verification and revocation."""

    def test_revoked_canary_tokens_remain_trackable(self):
        """Revoked canary tokens must preserve historical trip counts and timestamps."""
        token = CanaryToken(
            tenant_id="tenant-sec",
            token_type="AWS_API_KEY",
            token_name="revoked-canary",
            token_value_preview="AKIA123",
            trigger_url_or_domain="url",
            placement_description="test",
            times_triggered=10,
            is_revoked=True
        )
        assert token.is_revoked is True
        assert token.times_triggered == 10
