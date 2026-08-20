"""
tests/security/test_phase5_security.py
======================================
Phase 5 Security Tests: Forged SSO Token Defense, SCIM Auth & Session Hijacking Safeguards.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import Request
from backend.app.services.sso_service import SSOService
from backend.app.services.scim_service import SCIMService
from backend.app.core.exceptions import AuthenticationError


@pytest.mark.asyncio
async def test_forged_sso_empty_auth_code_rejected():
    """Forged SSO callback without IdP authorization code must fail with AuthenticationError."""
    db = AsyncMock()

    with pytest.raises(AuthenticationError, match="authorization code"):
        await SSOService.validate_sso_callback(
            db=db,
            organization_id="org-acme",
            received_state="state_valid",
            expected_state="state_valid",
            auth_code=""
        )


@pytest.mark.asyncio
async def test_scim_unauthorized_token_rejected():
    """Invalid SCIM bearer token must return None."""
    db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none = MagicMock(return_value=None)
    db.execute = AsyncMock(return_value=mock_res)

    result = await SCIMService.authenticate_scim_request(db, "bad_bearer_token")
    assert result is None
