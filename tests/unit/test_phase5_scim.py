"""
tests/unit/test_phase5_scim.py
==============================
Unit tests for Phase 5 SCIM 2.0 Identity Provisioning (RFC 7644).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.scim_service import SCIMService
from backend.app.models.scim import SCIMConfiguration


@pytest.mark.asyncio
async def test_scim_configuration_generation():
    """Validates creation of SCIM endpoints and bearer token hashing."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))

    config, token = await SCIMService.configure_scim(db, "org-acme-prod")
    assert token.startswith("scim_")
    assert config.bearer_token_hash == SCIMService._hash_token(token)


@pytest.mark.asyncio
async def test_scim_user_provisioning():
    """Validates automated user account creation from SCIM payload."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))

    scim_payload = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "userName": "alice.security@enterprise.com",
        "displayName": "Alice Security",
        "emails": [{"value": "alice.security@enterprise.com", "primary": True}],
        "active": True
    }

    result = await SCIMService.provision_user(db, "org-acme-prod", scim_payload)
    assert result["userName"] == "alice.security@enterprise.com"
    assert result["active"] is True
    assert db.add.called
