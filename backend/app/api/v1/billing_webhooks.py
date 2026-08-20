import logging
from fastapi import APIRouter, Request, Header, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.services.billing_provider import get_billing_provider
from backend.app.core.exceptions import SentinelAIException

logger = logging.getLogger("SentinelAI.BillingWebhook")

router = APIRouter(prefix="/billing", tags=["Billing Webhooks"])


@router.post("/webhook", status_code=status.HTTP_200_OK, summary="Process Inbound Billing Webhook")
async def process_billing_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Receives external billing webhook events, verifies HMAC cryptographic signatures,
    enforces replay prevention & idempotency, and updates customer subscription status.
    """
    payload_bytes = await request.body()
    signature = (
        request.headers.get("Sentinel-Signature") or
        request.headers.get("Stripe-Signature") or
        request.headers.get("X-Webhook-Signature", "")
    )

    provider = get_billing_provider()
    result = await provider.handle_webhook_event(db, payload_bytes, signature)
    await db.commit()
    return result
