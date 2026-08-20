"""
tests/unit/test_phase5_sso.py
=============================
Unit tests for Phase 5 Enterprise SSO (OIDC / SAML 2.0).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.sso_service import SSOService
from backend.app.models.identity import IdentityProvider
from backend.app.core.exceptions import AuthenticationError


@pytest.mark.asyncio
async def test_sso_authorization_url_generation():
    """Validates generation of OIDC authorization URL with state and nonce."""
    db = AsyncMock()
    mock_idp = IdentityProvider(
        organization_id="org-acme",
        provider_type="OIDC",
        name="Okta SSO",
        client_id="client_12345",
        sso_url="https://acme.okta.com/oauth2/v1/authorize",
        is_active=True
    )
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_idp)))

    res = await SSOService.generate_sso_authorization_url(
        db=db,
        organization_id="org-acme",
        redirect_uri="https://app.sentinelai.io/api/v1/identity/sso/callback"
    )

    assert "authorization_url" in res
    assert "state=" in res["authorization_url"]
    assert "nonce=" in res["authorization_url"]
    assert res["state"] is not None


@pytest.mark.asyncio
async def test_sso_state_mismatch_rejected():
    """State mismatch must fail with AuthenticationError (anti-CSRF protection)."""
    db = AsyncMock()

    with pytest.raises(AuthenticationError, match="state"):
        await SSOService.validate_sso_callback(
            db=db,
            organization_id="org-acme",
            received_state="state_bad",
            expected_state="state_good",
            auth_code="code_123"
        )
