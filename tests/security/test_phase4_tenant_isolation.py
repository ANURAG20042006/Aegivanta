"""
tests/security/test_phase4_tenant_isolation.py
==============================================
Phase 4 Security Tests: Cross-Tenant Data Isolation and Authorization Guardrails.
Verifies that Tenant A cannot access Tenant B resources under any circumstances.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import Request
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.models.user import User
from backend.app.models.tenant import TenantMembership
from backend.app.core.exceptions import PermissionDeniedError


@pytest.mark.asyncio
async def test_cross_tenant_header_spoofing_blocked():
    """Client-supplied X-Tenant-ID for an unassigned tenant must be rejected with PermissionDeniedError."""
    # User belongs only to tenant-alpha
    user = User(id="user-1", username="analyst_alpha", role="analyst", is_active=True)

    membership_alpha = TenantMembership(
        user_id="user-1",
        organization_id="org-alpha",
        tenant_id="tenant-alpha",
        role="SECURITY_ANALYST",
        status="ACTIVE"
    )

    db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[membership_alpha])))
    db.execute = AsyncMock(return_value=mock_res)

    # Request attempts to access tenant-bravo via X-Tenant-ID header
    request = MagicMock(spec=Request)
    request.headers = {"X-Tenant-ID": "tenant-bravo"}
    request.query_params = {}

    with pytest.raises(PermissionDeniedError, match="Access denied to tenant 'tenant-bravo'"):
        await resolve_tenant_context(request=request, current_user=user, db=db)
