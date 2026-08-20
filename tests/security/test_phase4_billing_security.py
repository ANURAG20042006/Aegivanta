"""
tests/security/test_phase4_billing_security.py
==============================================
Phase 4 Security Tests: Billing Webhook Signature Validation & Replay Attack Defense.
"""

import hmac
import hashlib
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.billing_provider import MockBillingProvider
from backend.app.models.billing import BillingWebhookEvent


@pytest.mark.asyncio
async def test_replay_webhook_idempotency_defense():
    """Duplicate/replayed webhook events with identical event_id must be safely ignored."""
    provider = MockBillingProvider(webhook_secret="test_secret")
    db = AsyncMock()

    # Mock that event_id already exists in database
    mock_res = MagicMock()
    mock_res.scalar_one_or_none = MagicMock(return_value=BillingWebhookEvent(event_id="evt_replay_123"))
    db.execute = AsyncMock(return_value=mock_res)

    payload = b'{"type": "invoice.paid", "id": "evt_replay_123"}'
    sig = hmac.new(b"test_secret", payload, hashlib.sha256).hexdigest()

    result = await provider.handle_webhook_event(db, payload, sig)
    assert result["status"] == "duplicate"
