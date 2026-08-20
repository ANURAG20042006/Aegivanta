"""
tests/security/test_phase4_api_key_security.py
==============================================
Phase 4 Security Tests: API Key Expiration, IP Whitelisting & Hash Verification.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.api_key_service import ApiKeyService
from backend.app.models.api_key import ApiKey


@pytest.mark.asyncio
async def test_expired_api_key_rejected():
    """Expired API key must return None (fail closed)."""
    db = AsyncMock()
    mock_token = "sk_live_" + "testmockdummytoken00000000000000"
    expired_key = ApiKey(
        key_prefix=mock_token[:14],
        hashed_secret="fake_hash",
        is_active=True,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1)
    )

    mock_res = MagicMock()
    mock_res.scalar_one_or_none = MagicMock(return_value=expired_key)
    db.execute = AsyncMock(return_value=mock_res)

    auth_result = await ApiKeyService.authenticate_key(db, mock_token)
    assert auth_result is None


@pytest.mark.asyncio
async def test_ip_restricted_api_key_blocked():
    """API key with IP restrictions must reject unauthorized client IPs."""
    db = AsyncMock()
    mock_token = "sk_live_" + "testmockdummytoken00000000000000"
    restricted_key = ApiKey(
        key_prefix=mock_token[:14],
        hashed_secret="fake_hash",
        is_active=True,
        ip_restrictions={"allowed_ips": ["192.168.1.100"]}
    )

    mock_res = MagicMock()
    mock_res.scalar_one_or_none = MagicMock(return_value=restricted_key)
    db.execute = AsyncMock(return_value=mock_res)

    auth_result = await ApiKeyService.authenticate_key(
        db, mock_token, client_ip="10.0.0.99"
    )
    assert auth_result is None

