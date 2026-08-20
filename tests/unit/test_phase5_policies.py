"""
tests/unit/test_phase5_policies.py
==================================
Unit tests for Phase 5 Security Policy Engine & Enforcement.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.security_policy_service import SecurityPolicyService
from backend.app.models.security_policy import SecurityPolicy


@pytest.mark.asyncio
async def test_policy_ip_denylist_enforcement():
    """Validates that login attempts from denylisted IP ranges are blocked."""
    db = AsyncMock()
    mock_policy = SecurityPolicy(
        organization_id="org-acme",
        ip_denylist={"ips": ["198.51.100.0/24"]}
    )
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_policy)))

    allowed, reason = await SecurityPolicyService.evaluate_login_policy(
        db=db,
        organization_id="org-acme",
        client_ip="198.51.100.42"
    )

    assert allowed is False
    assert "denylist" in reason


@pytest.mark.asyncio
async def test_policy_mfa_requirement_enforcement():
    """Validates that login is denied if organization policy mandates MFA and user is not MFA-verified."""
    db = AsyncMock()
    mock_policy = SecurityPolicy(
        organization_id="org-acme",
        require_mfa=True
    )
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_policy)))

    allowed, reason = await SecurityPolicyService.evaluate_login_policy(
        db=db,
        organization_id="org-acme",
        client_ip="10.0.0.1",
        is_mfa_authenticated=False
    )

    assert allowed is False
    assert "Multi-Factor Authentication" in reason
