import hashlib
import secrets
import logging
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any, Callable
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.api_key import ApiKey, ApiKeyScope
from backend.app.core.tenant import TenantContext, set_tenant_context
from backend.app.core.exceptions import AuthenticationError, PermissionDeniedError

logger = logging.getLogger("SentinelAI.ApiKey")

api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


class ApiKeyService:
    """Service for securely issuing, validating, and revoking customer API keys."""

    PREFIX = "sk_live_"

    @classmethod
    def _hash_key(cls, raw_secret: str) -> str:
        """Computes SHA-256 digest of secret token."""
        return hashlib.sha256(raw_secret.encode("utf-8")).hexdigest()

    @classmethod
    async def create_api_key(
        cls,
        db: AsyncSession,
        tenant_id: str,
        name: str,
        scopes: List[str],
        user_id: Optional[str] = None,
        rate_limit_rpm: int = 60,
        ip_restrictions: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None
    ) -> Tuple[ApiKey, str]:
        """
        Creates a new API key record. Returns the ApiKey ORM model and the full plaintext secret.
        The plaintext secret must only be returned to the client once.
        """
        # Generate 32 bytes of cryptographically secure random token
        random_suffix = secrets.token_hex(24)
        raw_key = f"{cls.PREFIX}{random_suffix}"
        key_prefix = raw_key[:14]  # e.g., "sk_live_a1b2c3"
        hashed = cls._hash_key(raw_key)

        api_key = ApiKey(
            tenant_id=tenant_id,
            created_by_user_id=user_id,
            name=name,
            key_prefix=key_prefix,
            hashed_secret=hashed,
            scopes={"scopes": scopes},
            rate_limit_rpm=rate_limit_rpm,
            ip_restrictions={"allowed_ips": ip_restrictions} if ip_restrictions else None,
            is_active=True,
            expires_at=expires_at
        )
        db.add(api_key)
        await db.flush()
        return api_key, raw_key

    @classmethod
    async def authenticate_key(
        cls,
        db: AsyncSession,
        raw_key: str,
        client_ip: Optional[str] = None
    ) -> Optional[ApiKey]:
        """Validates raw API key string against stored SHA-256 hash, expiration, and IP rules."""
        if not raw_key or not raw_key.startswith(cls.PREFIX):
            return None

        key_prefix = raw_key[:14]
        hashed = cls._hash_key(raw_key)

        stmt = select(ApiKey).where(
            and_(
                ApiKey.key_prefix == key_prefix,
                ApiKey.hashed_secret == hashed,
                ApiKey.is_active == True
            )
        )
        result = await db.execute(stmt)
        key_record = result.scalar_one_or_none()

        if not key_record:
            return None

        # Check expiration
        if key_record.expires_at and key_record.expires_at < datetime.now(timezone.utc):
            logger.warning("Attempted use of expired API key: %s", key_prefix)
            return None

        # Check IP restrictions if configured
        if key_record.ip_restrictions and client_ip:
            allowed = key_record.ip_restrictions.get("allowed_ips", [])
            if allowed and client_ip not in allowed:
                logger.warning("API key %s rejected from disallowed IP %s", key_prefix, client_ip)
                return None

        # Update last_used_at
        key_record.last_used_at = datetime.now(timezone.utc)
        await db.flush()
        return key_record

    @classmethod
    async def revoke_api_key(
        cls,
        db: AsyncSession,
        api_key_id: str,
        tenant_id: str
    ) -> bool:
        """Revokes an API key belonging to a tenant."""
        stmt = select(ApiKey).where(
            and_(
                ApiKey.id == api_key_id,
                ApiKey.tenant_id == tenant_id
            )
        )
        res = await db.execute(stmt)
        key = res.scalar_one_or_none()
        if not key:
            return False

        key.is_active = False
        await db.flush()
        return True


async def get_api_key_context(
    request: Request,
    api_key_header: Optional[str] = Depends(api_key_header_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[TenantContext]:
    """Resolves TenantContext if request is authenticated via X-API-Key or Bearer sk_live_..."""
    raw_key = api_key_header
    if not raw_key:
        auth_hdr = request.headers.get("Authorization", "")
        if auth_hdr.startswith("Bearer sk_live_"):
            raw_key = auth_hdr.replace("Bearer ", "").strip()

    if not raw_key:
        return None

    client_ip = request.client.host if request.client else "127.0.0.1"
    key_record = await ApiKeyService.authenticate_key(db, raw_key, client_ip)
    if not key_record:
        raise AuthenticationError(detail="Invalid or expired API Key.")

    scopes_list = key_record.scopes.get("scopes", []) if isinstance(key_record.scopes, dict) else []

    context = TenantContext(
        tenant_id=key_record.tenant_id,
        role="API_ADMIN" if "ADMIN" in scopes_list else "API_CLIENT",
        scopes=scopes_list,
        is_api_key_auth=True,
        api_key_id=key_record.id
    )
    set_tenant_context(context)
    return context


def require_api_key_scope(required_scope: ApiKeyScope) -> Callable:
    """Dependency that enforces required API key scope."""
    async def scope_guard(
        request: Request,
        key_context: Optional[TenantContext] = Depends(get_api_key_context)
    ) -> None:
        if not key_context:
            return  # Will be caught by main auth if user auth is used instead
        if "ADMIN" in key_context.scopes or required_scope.value in key_context.scopes:
            return
        raise PermissionDeniedError(detail=f"API key lacks required scope: '{required_scope.value}'")

    return scope_guard
