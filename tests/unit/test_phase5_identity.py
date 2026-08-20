"""
tests/unit/test_phase5_identity.py
==================================
Unit tests for Phase 5 Enterprise Identity: RFC 6238 TOTP MFA, Recovery Codes & Sessions.
"""

import pytest
import time
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.identity_service import IdentityService
from backend.app.models.identity import UserSession, MFAEnrollment


def test_totp_secret_and_code_generation():
    """Validates RFC 6238 TOTP computation and verification."""
    secret = IdentityService.generate_totp_secret()
    assert len(secret) >= 16

    code = IdentityService.compute_totp(secret)
    assert len(code) == 6
    assert code.isdigit()

    assert IdentityService.verify_totp(secret, code) is True
    assert IdentityService.verify_totp(secret, "000000") is False


def test_recovery_codes_generation():
    """Validates generation of single-use emergency recovery codes."""
    plain, hashed = IdentityService.generate_recovery_codes(count=8)
    assert len(plain) == 8
    assert len(hashed) == 8

    # Verify hashing
    for p, h in zip(plain, hashed):
        assert IdentityService._hash_token(p) == h


@pytest.mark.asyncio
async def test_create_user_session():
    """Validates session creation with IP tracking and device fingerprinting."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))

    session, raw_token = await IdentityService.create_user_session(
        db=db,
        user_id="usr-123",
        organization_id="org-123",
        ip_address="192.168.1.50",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )

    assert raw_token.startswith("sess_")
    assert session.user_id == "usr-123"
    assert session.is_active is True
    assert session.device_fingerprint is not None
