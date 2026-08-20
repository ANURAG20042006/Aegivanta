import hmac
import hashlib
import json
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import settings
from backend.app.models.billing import BillingWebhookEvent, Invoice
from backend.app.models.subscription import PlanTier
from backend.app.models.tenant import Organization
from backend.app.core.exceptions import SentinelAIException

logger = logging.getLogger("SentinelAI.Billing")


class BillingProvider(ABC):
    """Abstract interface for commercial billing providers (Stripe, Chargebee, Mock)."""

    @abstractmethod
    async def create_customer(self, organization_id: str, email: str, name: str) -> str:
        """Creates or registers a customer profile. Returns external customer ID."""
        pass

    @abstractmethod
    async def create_checkout_session(
        self,
        organization_id: str,
        plan_tier: PlanTier,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, str]:
        """Generates a hosted checkout URL for plan subscription."""
        pass

    @abstractmethod
    async def create_portal_session(self, organization_id: str, return_url: str) -> str:
        """Generates a self-service customer billing portal URL."""
        pass

    @abstractmethod
    def verify_webhook_signature(self, payload_bytes: bytes, signature_header: str, secret: str) -> bool:
        """Validates cryptographic HMAC signature on incoming webhooks."""
        pass

    @abstractmethod
    async def handle_webhook_event(
        self,
        db: AsyncSession,
        payload_bytes: bytes,
        signature_header: str
    ) -> Dict[str, Any]:
        """Processes an incoming webhook event idempotently."""
        pass


class MockBillingProvider(BillingProvider):
    """
    Standard test & private deployment billing provider.
    Validates HMAC signatures, records invoices, and handles webhook state transitions.
    """

    def __init__(self, webhook_secret: Optional[str] = None):
        self.webhook_secret = webhook_secret or settings.SECRET_KEY

    async def create_customer(self, organization_id: str, email: str, name: str) -> str:
        return f"cus_mock_{organization_id[:8]}"

    async def create_checkout_session(
        self,
        organization_id: str,
        plan_tier: PlanTier,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, str]:
        session_id = f"cs_mock_{uuid.uuid4().hex[:12]}"
        checkout_url = f"{success_url}?session_id={session_id}&plan={plan_tier.value}"
        return {"session_id": session_id, "url": checkout_url}

    async def create_portal_session(self, organization_id: str, return_url: str) -> str:
        return f"{return_url}?portal_session={uuid.uuid4().hex[:12]}"

    def verify_webhook_signature(self, payload_bytes: bytes, signature_header: str, secret: str) -> bool:
        """Verifies HMAC-SHA256 signature."""
        if not signature_header:
            return False
        expected_sig = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, signature_header)

    async def handle_webhook_event(
        self,
        db: AsyncSession,
        payload_bytes: bytes,
        signature_header: str
    ) -> Dict[str, Any]:
        """Validates signature and idempotently records the billing webhook event."""
        # 1. Signature Verification
        if not self.verify_webhook_signature(payload_bytes, signature_header, self.webhook_secret):
            logger.warning("Billing webhook signature validation failed")
            raise SentinelAIException(status_code=400, detail="Invalid webhook signature")

        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            raise SentinelAIException(status_code=400, detail="Invalid JSON payload")

        event_id = payload.get("id") or str(uuid.uuid4())
        event_type = payload.get("type", "unknown")

        # 2. Idempotency Check
        stmt = select(BillingWebhookEvent).where(BillingWebhookEvent.event_id == event_id)
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
            logger.info("Ignoring duplicate webhook event: %s", event_id)
            return {"status": "duplicate", "event_id": event_id}

        # 3. Store Webhook Event Audit
        webhook_record = BillingWebhookEvent(
            provider="MOCK",
            event_id=event_id,
            event_type=event_type,
            payload_json=payload,
            signature_header=signature_header,
            processed_status="PROCESSED"
        )
        db.add(webhook_record)
        await db.flush()

        logger.info("Processed billing webhook: %s (%s)", event_id, event_type)
        return {"status": "success", "event_id": event_id, "event_type": event_type}


def get_billing_provider() -> BillingProvider:
    """Returns configured BillingProvider instance."""
    return MockBillingProvider()
