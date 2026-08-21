"""
tests/unit/test_phase33_canary_tokens.py
========================================
Phase 33 Traceable Canary Token Unit Tests.
"""

import pytest
from backend.app.models.deception import CanaryToken


class TestCanaryTokens:
    """Unit tests for Canary Token schemas and trigger counts."""

    def test_canary_token_model(self):
        """CanaryToken must store token type, trigger URL, and placement description."""
        token = CanaryToken(
            tenant_id="tenant-123",
            token_type="AWS_API_KEY",
            token_name="ci-cd-prod-aws-key",
            token_value_preview="AKIAIOSFODNN7EXAMPLE",
            trigger_url_or_domain="https://canary.aegivanta.io/v1/ping/aws-k92",
            placement_description="Placed in /home/ubuntu/.aws/credentials",
            times_triggered=3,
            is_revoked=False
        )
        assert token.token_type == "AWS_API_KEY"
        assert "AKIA" in token.token_value_preview
        assert token.times_triggered == 3
