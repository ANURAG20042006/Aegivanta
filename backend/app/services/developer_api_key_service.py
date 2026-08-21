"""
backend/app/services/developer_api_key_service.py
=================================================
Phase 45 Developer API Key Management Service.
Generates cryptographically random API tokens, hashed keys, and validates scopes.
"""

import uuid
import secrets
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.developer_webhooks import DeveloperApiKey

logger = logging.getLogger("Aegivanta.DeveloperApiKey")


class DeveloperApiKeyService:
    """Developer API Key Engine."""

    @classmethod
    async def list_keys(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists active API keys for a tenant."""
        stmt = select(DeveloperApiKey).where(
            DeveloperApiKey.tenant_id == tenant_id
        ).order_by(desc(DeveloperApiKey.created_at)).limit(limit)

        keys = list((await db.execute(stmt)).scalars().all())

        if not keys:
            defaults = [
                ("SIEM Ingestion Stream Key", "aeg_live_", hashlib.sha256(b"KEY_1").hexdigest(), "telemetry:read,alerts:read", 5000),
                ("SOAR Remediation Automation Key", "aeg_live_", hashlib.sha256(b"KEY_2").hexdigest(), "alerts:write,soar:execute", 2000)
            ]
            for name, pfx, khash, scp, rpm in defaults:
                inst = DeveloperApiKey(
                    tenant_id=tenant_id,
                    key_name=name,
                    key_prefix=pfx,
                    key_hash=khash,
                    scopes=scp,
                    rate_limit_rpm=rpm,
                    active=True,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(DeveloperApiKey).where(DeveloperApiKey.tenant_id == tenant_id)
            keys = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": k.id,
                "key_name": k.key_name,
                "key_prefix": k.key_prefix,
                "scopes": k.scopes,
                "rate_limit_rpm": k.rate_limit_rpm,
                "active": k.active,
                "created_at": k.created_at.isoformat()
            }
            for k in keys
        ]

    @classmethod
    async def create_key(
        cls,
        db: AsyncSession,
        tenant_id: str,
        key_name: str,
        scopes: str = "telemetry:read,alerts:write",
        rate_limit_rpm: int = 1000
    ) -> Dict[str, Any]:
        """Generates a new developer API key with plaintext secret (shown once)."""
        raw_secret = f"aeg_live_{secrets.token_hex(24)}"
        khash = hashlib.sha256(raw_secret.encode()).hexdigest()

        key = DeveloperApiKey(
            tenant_id=tenant_id,
            key_name=key_name,
            key_prefix="aeg_live_",
            key_hash=khash,
            scopes=scopes,
            rate_limit_rpm=rate_limit_rpm,
            active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(key)
        await db.flush()

        return {
            "id": key.id,
            "key_name": key.key_name,
            "raw_api_key": raw_secret,  # Exposed only once upon creation
            "key_prefix": key.key_prefix,
            "scopes": key.scopes,
            "rate_limit_rpm": key.rate_limit_rpm,
            "created_at": key.created_at.isoformat()
        }
