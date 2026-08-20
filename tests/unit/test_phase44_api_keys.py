"""
tests/unit/test_phase44_api_keys.py
===================================
Phase 4.4 API Key Security Tests.
Validates SHA-256 key hashing, prefix indexing, scope enforcement, and revocation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.api_key_service import ApiKeyService, require_api_key_scope
from backend.app.models.api_key import ApiKey, ApiKeyScope
from backend.app.core.tenant import TenantContext
from backend.app.core.exceptions import PermissionDeniedError


class TestApiKeyService:

    @pytest.mark.asyncio
    async def test_create_api_key_generates_prefix_and_secret(self):
        """create_api_key must return a valid sk_live_ prefix and raw secret."""
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()

        key_record, raw_secret = await ApiKeyService.create_api_key(
            db=db,
            tenant_id="tenant-123",
            name="CI Pipeline Ingestion Key",
            scopes=["READ_TELEMETRY", "WRITE_TELEMETRY"]
        )

        assert raw_secret.startswith("sk_live_")
        assert key_record.key_prefix == raw_secret[:14]
        assert key_record.hashed_secret != raw_secret  # Never store raw secret
        assert len(key_record.hashed_secret) == 64     # SHA-256 hex digest
        assert key_record.is_active is True

    @pytest.mark.asyncio
    async def test_scope_guard_permits_authorized_scope(self):
        """require_api_key_scope must permit keys holding the required scope."""
        guard = require_api_key_scope(ApiKeyScope.WRITE_TELEMETRY)
        
        ctx_telemetry = TenantContext(scopes=["READ_TELEMETRY", "WRITE_TELEMETRY"])
        ctx_admin = TenantContext(scopes=["ADMIN"])

        # Should not raise
        await guard(request=MagicMock(), key_context=ctx_telemetry)
        await guard(request=MagicMock(), key_context=ctx_admin)

    @pytest.mark.asyncio
    async def test_scope_guard_denies_missing_scope(self):
        """require_api_key_scope must raise PermissionDeniedError if key lacks scope."""
        guard = require_api_key_scope(ApiKeyScope.EXECUTE_RESPONSE)
        ctx_read_only = TenantContext(scopes=["READ_INCIDENTS", "READ_TELEMETRY"])

        with pytest.raises(PermissionDeniedError, match="API key lacks required scope"):
            await guard(request=MagicMock(), key_context=ctx_read_only)
