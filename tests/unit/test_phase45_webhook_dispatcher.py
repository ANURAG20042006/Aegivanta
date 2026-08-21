"""
tests/unit/test_phase45_webhook_dispatcher.py
=============================================
Phase 45 Webhook Dispatcher & Subscription Unit Tests.
"""

import pytest
from backend.app.models.developer_webhooks import WebhookSubscription, WebhookDeliveryLog


class TestWebhookDispatcher:
    """Unit tests for WebhookSubscription and DeliveryLog models."""

    def test_webhook_subscription_model_creation(self):
        """WebhookSubscription must store endpoint URL, subscribed events, and secret token."""
        sub = WebhookSubscription(
            tenant_id="tenant-dev",
            endpoint_url="https://api.enterprise-soc.com/webhooks/aegivanta-alerts",
            subscribed_events="alert.created,threat.blocked",
            secret_token="whsec_01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6",
            active=True,
            retry_count_max=5
        )
        assert sub.endpoint_url == "https://api.enterprise-soc.com/webhooks/aegivanta-alerts"
        assert sub.subscribed_events == "alert.created,threat.blocked"
        assert sub.retry_count_max == 5
