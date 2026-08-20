"""
tests/unit/test_phase4_api_keys.py
==================================
Unit tests for Phase 4 API Key Cryptography and Expiration.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.api_key_service import ApiKeyService


@pytest.mark.asyncio
async def test_api_key_crypto_entropy():
    """Validates that generated API keys contain high entropy and proper prefixes."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()

    key_record, secret = await ApiKeyService.create_api_key(
        db=db,
        tenant_id="ten-prod",
        name="Telemetry Ingestion Key",
        scopes=["WRITE_TELEMETRY"],
        expires_at=datetime.now(timezone.utc) + timedelta(days=90)
    )

    assert secret.startswith("sk_live_")
    assert len(secret) > 40
    assert key_record.hashed_secret == ApiKeyService._hash_key(secret)
