"""
tests/unit/test_phase45_models.py
=================================
Phase 45 Model Schema & Attributes Unit Tests.
"""

import pytest
from backend.app.models.developer_webhooks import (
    DeveloperApiKey, WebhookSubscription, WebhookDeliveryLog
)


class TestPhase45Models:
    """Unit tests verifying Phase 45 database attributes."""

    def test_webhook_delivery_log_attributes(self):
        """Webhook delivery log should store duration, status, and payload."""
        log = WebhookDeliveryLog(
            tenant_id="tenant-dev",
            subscription_id="sub-123",
            event_type="alert.created",
            payload_json={"test": True},
            response_status=200,
            duration_ms=42.5,
            status="DELIVERED"
        )
        assert log.response_status == 200
        assert log.status == "DELIVERED"
        assert log.duration_ms == 42.5
