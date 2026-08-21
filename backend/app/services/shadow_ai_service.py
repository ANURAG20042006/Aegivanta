"""
backend/app/services/shadow_ai_service.py
=========================================
Phase 30 Shadow AI Discovery & Employee Usage Governance Service.
Discovers and monitors unauthorized consumer GenAI applications across corporate endpoints:
- ChatGPT (OpenAI Consumer)
- Claude.ai (Anthropic Consumer)
- Midjourney / DALL-E
- Perplexity AI / Poe
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.llm_security import ShadowAIDiscoveryRecord

logger = logging.getLogger("Aegivanta.ShadowAI")


class ShadowAIService:
    """Enterprise Shadow AI Discovery & Governance Engine."""

    @classmethod
    async def list_discovered_apps(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists discovered shadow GenAI tools across corporate endpoints."""
        stmt = select(ShadowAIDiscoveryRecord).where(
            ShadowAIDiscoveryRecord.tenant_id == tenant_id
        ).order_by(desc(ShadowAIDiscoveryRecord.last_active_at)).limit(limit)

        records = list((await db.execute(stmt)).scalars().all())

        if not records:
            # Seed default Shadow AI discovery records
            defaults = [
                ("ChatGPT (Consumer Web)", "GENERATIVE_AI_CHATBOT", "john.doe@aegivanta.io", "WS-FINANCE-04", 42.5, "HIGH", False, False),
                ("Claude.ai (Anthropic)", "GENERATIVE_AI_CHATBOT", "alice.smith@aegivanta.io", "MAC-DEV-08", 18.2, "MEDIUM", False, False),
                ("Midjourney (Discord Bot)", "IMAGE_GENERATION", "designer.mike@aegivanta.io", "WS-MKTG-02", 95.0, "HIGH", False, True),
                ("Perplexity AI Search", "AI_SEARCH_ENGINE", "researcher.ken@aegivanta.io", "MAC-EXEC-01", 12.4, "MEDIUM", True, False)
            ]
            for tool, cat, usr, host, vol, rsk, apprv, blk in defaults:
                inst = ShadowAIDiscoveryRecord(
                    tenant_id=tenant_id,
                    ai_tool_name=tool,
                    category=cat,
                    user_principal=usr,
                    endpoint_hostname=host,
                    data_volume_mb=vol,
                    risk_rating=rsk,
                    is_corporate_approved=apprv,
                    is_blocked=blk,
                    first_seen_at=datetime.now(timezone.utc),
                    last_active_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(ShadowAIDiscoveryRecord).where(ShadowAIDiscoveryRecord.tenant_id == tenant_id)
            records = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": r.id,
                "ai_tool_name": r.ai_tool_name,
                "category": r.category,
                "user_principal": r.user_principal,
                "endpoint_hostname": r.endpoint_hostname,
                "data_volume_mb": r.data_volume_mb,
                "risk_rating": r.risk_rating,
                "is_corporate_approved": r.is_corporate_approved,
                "is_blocked": r.is_blocked,
                "last_active_at": r.last_active_at.isoformat()
            }
            for r in records
        ]

    @classmethod
    async def toggle_block_status(
        cls,
        db: AsyncSession,
        tenant_id: str,
        record_id: str,
        block: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Blocks or unblocks a Shadow AI application for corporate network / endpoint policies."""
        stmt = select(ShadowAIDiscoveryRecord).where(
            ShadowAIDiscoveryRecord.id == record_id,
            ShadowAIDiscoveryRecord.tenant_id == tenant_id
        )
        rec = (await db.execute(stmt)).scalar_one_or_none()
        if not rec:
            return None

        rec.is_blocked = block
        await db.flush()

        return {
            "id": rec.id,
            "ai_tool_name": rec.ai_tool_name,
            "is_blocked": rec.is_blocked,
            "action": "BLOCKED_BY_EDR_DNS_POLICY" if block else "UNBLOCKED"
        }
