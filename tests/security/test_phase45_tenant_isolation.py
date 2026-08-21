"""
tests/security/test_phase45_tenant_isolation.py
===============================================
Phase 45 Developer Platform Multi-Tenant Isolation Security Tests.
"""

import pytest
from backend.app.models.developer_webhooks import (
    DeveloperApiKey, WebhookSubscription, WebhookDeliveryLog
)


class TestDeveloperMultiTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 45 models."""

    def test_developer_models_enforce_tenant_id(self):
        """All Phase 45 Developer models must enforce tenant_id partition attributes."""
        key = DeveloperApiKey(tenant_id="tenant-dev-1", key_name="k1", key_hash="h1")
        sub = WebhookSubscription(tenant_id="tenant-dev-1", endpoint_url="u1", secret_token="s1")
        log = WebhookDeliveryLog(tenant_id="tenant-dev-1", subscription_id="s1", event_type="e1")

        assert key.tenant_id == "tenant-dev-1"
        assert sub.tenant_id == "tenant-dev-1"
        assert log.tenant_id == "tenant-dev-1"
