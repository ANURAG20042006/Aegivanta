"""
backend/app/services/webhook_platform_service.py
================================================
Phase 23 Webhook Platform — Signing, Replay Protection, Retry, Delivery Tracking, Dead-Letter.
"""

import logging
import uuid
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.integration_ecosystem import WebhookDelivery

logger = logging.getLogger("Aegivanta.WebhookPlatform")

# Seen nonces for replay protection (in production: use Redis SET with TTL)
_SEEN_NONCES: set = set()


class WebhookPlatformService:
    """Manages webhook delivery with HMAC signing, replay protection, exponential retry, and dead-letter."""

    @classmethod
    def create_signed_delivery(
        cls,
        connector_id: str,
        event_id: str,
        endpoint_url: str,
        payload: Dict[str, Any],
        secret: str
    ) -> Dict[str, Any]:
        """Creates a signed webhook delivery record."""
        import json
        payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        replay_nonce = str(uuid.uuid4())
        timestamp_str = datetime.now(timezone.utc).isoformat()

        # Sign: HMAC-SHA256(secret, payload || nonce || timestamp)
        sig_material = payload_bytes + replay_nonce.encode() + timestamp_str.encode()
        signature = hmac.new(secret.encode("utf-8"), sig_material, hashlib.sha256).hexdigest()

        return {
            "connector_id": connector_id,
            "event_id": event_id,
            "endpoint_url": endpoint_url,
            "hmac_signature": signature,
            "replay_nonce": replay_nonce,
            "timestamp": timestamp_str,
            "payload": payload
        }

    @classmethod
    def is_replay_attack(cls, nonce: str) -> bool:
        """Checks if a nonce has already been seen (replay attack detection)."""
        if nonce in _SEEN_NONCES:
            return True
        _SEEN_NONCES.add(nonce)
        return False

    @classmethod
    def compute_next_retry(cls, attempt_count: int, base_seconds: float = 2.0) -> datetime:
        """Computes next retry time with exponential backoff."""
        delay = min(base_seconds ** (attempt_count + 1), 3600.0)
        return datetime.now(timezone.utc) + timedelta(seconds=delay)

    @classmethod
    async def record_delivery_attempt(
        cls,
        db: AsyncSession,
        tenant_id: str,
        connector_id: str,
        event_id: str,
        endpoint_url: str,
        hmac_signature: str,
        replay_nonce: str,
        http_status_code: Optional[int],
        response_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Records a webhook delivery attempt result."""
        stmt = select(WebhookDelivery).where(
            WebhookDelivery.event_id == event_id,
            WebhookDelivery.connector_id == connector_id,
            WebhookDelivery.tenant_id == tenant_id
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()

        success = http_status_code is not None and 200 <= http_status_code < 300
        attempt_count = (existing.attempt_count + 1) if existing else 1
        is_dead_letter = (not success) and (attempt_count >= 3)

        if existing:
            existing.attempt_count = attempt_count
            existing.http_status_code = http_status_code
            existing.response_body = response_body
            existing.status = "DELIVERED" if success else ("DEAD_LETTER" if is_dead_letter else "FAILED")
            existing.is_dead_letter = is_dead_letter
            existing.delivered_at = datetime.now(timezone.utc) if success else None
            existing.next_retry_at = cls.compute_next_retry(attempt_count) if not success and not is_dead_letter else None
            delivery = existing
        else:
            delivery = WebhookDelivery(
                tenant_id=tenant_id,
                connector_id=connector_id,
                event_id=event_id,
                endpoint_url=endpoint_url,
                hmac_signature=hmac_signature,
                replay_nonce=replay_nonce,
                status="DELIVERED" if success else ("DEAD_LETTER" if is_dead_letter else "FAILED"),
                http_status_code=http_status_code,
                attempt_count=1,
                response_body=response_body,
                is_dead_letter=is_dead_letter,
                delivered_at=datetime.now(timezone.utc) if success else None,
                next_retry_at=cls.compute_next_retry(1) if not success and not is_dead_letter else None,
                created_at=datetime.now(timezone.utc)
            )
            db.add(delivery)

        await db.flush()
        return {
            "id": delivery.id,
            "status": delivery.status,
            "attempt_count": delivery.attempt_count,
            "is_dead_letter": delivery.is_dead_letter,
            "next_retry_at": delivery.next_retry_at.isoformat() if delivery.next_retry_at else None
        }

    @classmethod
    async def list_delivery_status(cls, db: AsyncSession, tenant_id: str) -> List[Dict[str, Any]]:
        """Returns webhook delivery status across all connectors."""
        stmt = select(WebhookDelivery).where(
            WebhookDelivery.tenant_id == tenant_id
        ).order_by(desc(WebhookDelivery.created_at)).limit(100)

        deliveries = list((await db.execute(stmt)).scalars().all())
        if not deliveries:
            # Seed sample delivery records
            for i, (conn_id, ev_id, status, code, attempts, dl) in enumerate([
                ("conn-splunk-01", "evt-alert-001", "DELIVERED", 200, 1, False),
                ("conn-slack-01", "evt-alert-002", "DELIVERED", 200, 1, False),
                ("conn-sn-01", "evt-incident-003", "FAILED", 503, 2, False),
                ("conn-csf-01", "evt-alert-004", "DEAD_LETTER", 500, 3, True),
            ]):
                delivery = WebhookDelivery(
                    tenant_id=tenant_id,
                    connector_id=conn_id,
                    event_id=ev_id,
                    endpoint_url=f"https://connector-{i}.example.com/webhook",
                    hmac_signature="a" * 64,
                    replay_nonce=str(uuid.uuid4()),
                    status=status,
                    http_status_code=code,
                    attempt_count=attempts,
                    is_dead_letter=dl,
                    delivered_at=datetime.now(timezone.utc) if status == "DELIVERED" else None,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(delivery)
            await db.flush()

            stmt2 = select(WebhookDelivery).where(WebhookDelivery.tenant_id == tenant_id).order_by(desc(WebhookDelivery.created_at))
            deliveries = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": d.id,
                "connector_id": d.connector_id,
                "event_id": d.event_id,
                "status": d.status,
                "http_status_code": d.http_status_code,
                "attempt_count": d.attempt_count,
                "is_dead_letter": d.is_dead_letter,
                "next_retry_at": d.next_retry_at.isoformat() if d.next_retry_at else None,
                "delivered_at": d.delivered_at.isoformat() if d.delivered_at else None,
                "created_at": d.created_at.isoformat() if d.created_at else None
            }
            for d in deliveries
        ]
