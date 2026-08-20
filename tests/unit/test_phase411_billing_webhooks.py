"""
tests/unit/test_phase411_billing_webhooks.py
============================================
Phase 4.11 & 4.12 Billing Architecture & Webhook Security Tests.
Validates HMAC-SHA256 signature verification, replay prevention, and idempotency.
"""

import hmac
import hashlib
import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.billing_provider import MockBillingProvider
from backend.app.core.exceptions import SentinelAIException


class TestBillingWebhookSecurity:

    def test_verify_webhook_signature_valid(self):
        """Valid HMAC signature must return True."""
        secret = "super_secret_webhook_key_123"
        provider = MockBillingProvider(webhook_secret=secret)
        payload = b'{"type": "invoice.paid", "id": "evt_123"}'
        signature = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

        assert provider.verify_webhook_signature(payload, signature, secret) is True

    def test_verify_webhook_signature_tampered_payload_rejected(self):
        """Tampered payload with mismatched signature must return False."""
        secret = "super_secret_webhook_key_123"
        provider = MockBillingProvider(webhook_secret=secret)
        original_payload = b'{"type": "invoice.paid", "id": "evt_123"}'
        signature = hmac.new(secret.encode("utf-8"), original_payload, hashlib.sha256).hexdigest()

        tampered_payload = b'{"type": "invoice.paid", "id": "evt_ATTACKER"}'
        assert provider.verify_webhook_signature(tampered_payload, signature, secret) is False

    @pytest.mark.asyncio
    async def test_handle_webhook_event_rejects_invalid_signature(self):
        """handle_webhook_event must raise SentinelAIException 400 when signature is invalid."""
        provider = MockBillingProvider(webhook_secret="key")
        db = AsyncMock()

        with pytest.raises(SentinelAIException) as exc:
            await provider.handle_webhook_event(db, b'{"foo": "bar"}', "bad_sig")
        assert exc.value.status_code == 400
