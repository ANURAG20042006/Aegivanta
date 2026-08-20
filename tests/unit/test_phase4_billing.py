"""
tests/unit/test_phase4_billing.py
=================================
Unit tests for Phase 4 Billing Provider & Invoicing Abstraction.
"""

import pytest
from backend.app.services.billing_provider import MockBillingProvider, get_billing_provider
from backend.app.models.subscription import PlanTier


@pytest.mark.asyncio
async def test_billing_provider_checkout_generation():
    """Validates checkout session generation without vendor lock-in."""
    provider = get_billing_provider()
    session = await provider.create_checkout_session(
        organization_id="org-acme-123",
        plan_tier=PlanTier.PROFESSIONAL,
        success_url="https://app.sentinelai.io/billing/success",
        cancel_url="https://app.sentinelai.io/billing/cancel"
    )

    assert "session_id" in session
    assert "url" in session
    assert "cs_mock_" in session["session_id"]
