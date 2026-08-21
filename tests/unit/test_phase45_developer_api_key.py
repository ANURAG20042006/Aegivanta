"""
tests/unit/test_phase45_developer_api_key.py
============================================
Phase 45 Developer API Key Unit Tests.
"""

import pytest
from backend.app.models.developer_webhooks import DeveloperApiKey


class TestDeveloperApiKey:
    """Unit tests for DeveloperApiKey model."""

    def test_developer_api_key_model_creation(self):
        """DeveloperApiKey must store name, prefix, hash, scopes, and rate limit."""
        key = DeveloperApiKey(
            tenant_id="tenant-dev",
            key_name="SIEM Ingestion Stream Key",
            key_prefix="aeg_live_",
            key_hash="abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
            scopes="telemetry:read,alerts:read",
            rate_limit_rpm=5000,
            active=True
        )
        assert key.key_name == "SIEM Ingestion Stream Key"
        assert key.key_prefix == "aeg_live_"
        assert key.rate_limit_rpm == 5000
        assert key.active is True
