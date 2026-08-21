"""
backend/app/services/canary_token_service.py
============================================
Phase 33 Traceable Canary Token Generator & Trigger Processing Engine.
Generates:
- AWS IAM API Keys (Triggered upon sts:GetCallerIdentity or IAM calls)
- PDF/Word Document Webhooks (Triggered when opened by an attacker)
- DNS Canary Tokens (Triggered upon DNS resolution probe)
- Kubeconfig Canaries & Database Credentials
"""

import uuid
import secrets
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.deception import CanaryToken, DeceptionInteractionEvent

logger = logging.getLogger("Aegivanta.CanaryTokens")


class CanaryTokenService:
    """Enterprise Canary Token Generation & Tracking Engine."""

    @classmethod
    async def list_canary_tokens(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists active canary tokens."""
        stmt = select(CanaryToken).where(
            CanaryToken.tenant_id == tenant_id
        ).order_by(desc(CanaryToken.created_at)).limit(limit)

        tokens = list((await db.execute(stmt)).scalars().all())

        if not tokens:
            # Seed default canary tokens
            defaults = [
                ("AWS_API_KEY", "prod-deployer-aws-keys", "AKIAIOSFODNN7EXAMPLE", "https://canary.aegivanta.io/v1/ping/aws-k92", "Placed in /home/deploy/.aws/credentials on CI runner", 2),
                ("WEBHOOK_DOC", "2026_Executive_Compensation_Plan.docx", "CANARY_DOCX_TRACKER_V33", "https://canary.aegivanta.io/v1/ping/doc-f41", "Placed in Shared Financial Drive \\\\corp-fs\\finance", 5),
                ("DNS_BEACON", "internal-vault-db.canary.aegivanta.net", "DNS_CANARY_TOKEN_A89", "internal-vault-db.canary.aegivanta.net", "Injected in developer bash history on WS-DEV-04", 1)
            ]
            for t_type, name, prev, url, descr, trg in defaults:
                inst = CanaryToken(
                    tenant_id=tenant_id,
                    token_type=t_type,
                    token_name=name,
                    token_value_preview=prev,
                    trigger_url_or_domain=url,
                    placement_description=descr,
                    times_triggered=trg,
                    is_revoked=False,
                    created_at=datetime.now(timezone.utc),
                    last_triggered_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(CanaryToken).where(CanaryToken.tenant_id == tenant_id)
            tokens = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": t.id,
                "token_type": t.token_type,
                "token_name": t.token_name,
                "token_value_preview": t.token_value_preview,
                "trigger_url_or_domain": t.trigger_url_or_domain,
                "placement_description": t.placement_description,
                "times_triggered": t.times_triggered,
                "is_revoked": t.is_revoked,
                "created_at": t.created_at.isoformat(),
                "last_triggered_at": t.last_triggered_at.isoformat() if t.last_triggered_at else None
            }
            for t in tokens
        ]

    @classmethod
    async def generate_token(
        cls,
        db: AsyncSession,
        tenant_id: str,
        token_type: str,
        token_name: str,
        placement_description: str
    ) -> Dict[str, Any]:
        """Generates a new traceable canary token."""
        rand_id = secrets.token_hex(4)
        t_type = token_type.upper().strip()

        if t_type == "AWS_API_KEY":
            preview = f"AKIA{secrets.token_hex(8).upper()}"
            url = f"https://canary.aegivanta.io/v1/ping/aws-{rand_id}"
        elif t_type == "DNS_BEACON":
            preview = f"canary-{rand_id}.aegivanta-canary.net"
            url = preview
        else:
            preview = f"CANARY_HOOK_{rand_id.upper()}"
            url = f"https://canary.aegivanta.io/v1/ping/doc-{rand_id}"

        token = CanaryToken(
            tenant_id=tenant_id,
            token_type=t_type,
            token_name=token_name.strip(),
            token_value_preview=preview,
            trigger_url_or_domain=url,
            placement_description=placement_description.strip(),
            times_triggered=0,
            is_revoked=False,
            created_at=datetime.now(timezone.utc)
        )
        db.add(token)
        await db.flush()

        return {
            "id": token.id,
            "token_type": token.token_type,
            "token_name": token.token_name,
            "token_value_preview": token.token_value_preview,
            "trigger_url_or_domain": token.trigger_url_or_domain,
            "created_at": token.created_at.isoformat()
        }

    @classmethod
    async def process_canary_trigger(
        cls,
        db: AsyncSession,
        tenant_id: str,
        token_id: str,
        source_ip: str = "198.51.100.22"
    ) -> Optional[Dict[str, Any]]:
        """Processes a live canary token trip and generates critical interaction alert."""
        stmt = select(CanaryToken).where(
            CanaryToken.id == token_id,
            CanaryToken.tenant_id == tenant_id
        )
        token = (await db.execute(stmt)).scalar_one_or_none()
        if not token:
            return None

        token.times_triggered += 1
        token.last_triggered_at = datetime.now(timezone.utc)

        # Log DeceptionInteractionEvent
        event = DeceptionInteractionEvent(
            tenant_id=tenant_id,
            source_ip=source_ip,
            attacker_asn="AS14061 DigitalOcean, LLC",
            target_decoy_name=token.token_name,
            interaction_type="CANARY_TRIGGER",
            captured_payload_or_command=f"Canary token '{token.token_name}' accessed by remote principal at {source_ip}",
            mitre_engage_activity="EAC0004_EXPOSE",
            fidelity_confidence=100.0,
            containment_action_taken="IP_ISOLATED_BY_SOAR",
            occurred_at=datetime.now(timezone.utc)
        )
        db.add(event)
        await db.flush()

        return {
            "status": "CANARY_TRIGGERED",
            "token_id": token.id,
            "token_name": token.token_name,
            "times_triggered": token.times_triggered,
            "event_id": event.id,
            "action_taken": event.containment_action_taken
        }
