"""
tests/unit/test_phase4_tenant.py
================================
Unit tests for Phase 4 Multi-Tenant Resolution and Role Hierarchy.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.models.tenant import Organization, Tenant, TenantMembership, TenantRole, TenantSettings
from backend.app.core.tenant import (
    TenantContext,
    set_tenant_context,
    get_tenant_context,
    TENANT_ROLE_HIERARCHY,
    require_tenant_role
)
from backend.app.core.exceptions import PermissionDeniedError


def test_tenant_context_creation():
    """Validates creation and attributes of TenantContext."""
    ctx = TenantContext(
        user_id="usr-1",
        organization_id="org-1",
        tenant_id="ten-1",
        role=TenantRole.ADMIN.value,
        is_system_admin=False
    )
    assert ctx.user_id == "usr-1"
    assert ctx.organization_id == "org-1"
    assert ctx.tenant_id == "ten-1"
    assert ctx.role == "ADMIN"
    assert ctx.is_system_admin is False


def test_tenant_role_hierarchy():
    """Validates strict numerical ranking across all tenant roles."""
    assert TENANT_ROLE_HIERARCHY[TenantRole.OWNER.value] == 100
    assert TENANT_ROLE_HIERARCHY[TenantRole.ADMIN.value] == 80
    assert TENANT_ROLE_HIERARCHY[TenantRole.SECURITY_ANALYST.value] == 60
    assert TENANT_ROLE_HIERARCHY[TenantRole.RESPONDER.value] == 50
    assert TENANT_ROLE_HIERARCHY[TenantRole.API_ADMIN.value] == 40
    assert TENANT_ROLE_HIERARCHY[TenantRole.BILLING_ADMIN.value] == 30
    assert TENANT_ROLE_HIERARCHY[TenantRole.VIEWER.value] == 10


@pytest.mark.asyncio
async def test_require_tenant_role_owner_boundary():
    """Only OWNER or System Admin can access OWNER-restricted operations."""
    guard = require_tenant_role(TenantRole.OWNER)

    owner_ctx = TenantContext(role=TenantRole.OWNER.value)
    admin_ctx = TenantContext(role=TenantRole.ADMIN.value)

    assert await guard(owner_ctx) == owner_ctx

    with pytest.raises(PermissionDeniedError):
        await guard(admin_ctx)
