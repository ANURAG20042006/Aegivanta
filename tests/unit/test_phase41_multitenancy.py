"""
tests/unit/test_phase41_multitenancy.py
======================================
Phase 4.1 & 4.2 Multi-Tenancy & Organization Management Tests.
Validates tenant boundary resolution, role hierarchy, membership enforcement, and defense-in-depth.
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


class TestTenantContext:

    def test_tenant_context_storage_and_retrieval(self):
        """TenantContext must store and retrieve fields accurately via ContextVar."""
        ctx = TenantContext(
            user_id="user-123",
            organization_id="org-456",
            tenant_id="tenant-789",
            role=TenantRole.OWNER.value,
            is_system_admin=False
        )
        set_tenant_context(ctx)
        retrieved = get_tenant_context()

        assert retrieved is not None
        assert retrieved.user_id == "user-123"
        assert retrieved.organization_id == "org-456"
        assert retrieved.tenant_id == "tenant-789"
        assert retrieved.role == "OWNER"

    def test_tenant_role_hierarchy_order(self):
        """Role hierarchy must order OWNER > ADMIN > SECURITY_ANALYST > RESPONDER > VIEWER."""
        assert TENANT_ROLE_HIERARCHY[TenantRole.OWNER.value] > TENANT_ROLE_HIERARCHY[TenantRole.ADMIN.value]
        assert TENANT_ROLE_HIERARCHY[TenantRole.ADMIN.value] > TENANT_ROLE_HIERARCHY[TenantRole.SECURITY_ANALYST.value]
        assert TENANT_ROLE_HIERARCHY[TenantRole.SECURITY_ANALYST.value] > TENANT_ROLE_HIERARCHY[TenantRole.RESPONDER.value]
        assert TENANT_ROLE_HIERARCHY[TenantRole.RESPONDER.value] > TENANT_ROLE_HIERARCHY[TenantRole.VIEWER.value]

    @pytest.mark.asyncio
    async def test_require_tenant_role_permits_sufficient_role(self):
        """require_tenant_role must permit users with equal or higher role level."""
        guard = require_tenant_role(TenantRole.SECURITY_ANALYST)
        
        ctx_analyst = TenantContext(role=TenantRole.SECURITY_ANALYST.value)
        ctx_admin = TenantContext(role=TenantRole.ADMIN.value)
        ctx_owner = TenantContext(role=TenantRole.OWNER.value)

        assert await guard(ctx_analyst) == ctx_analyst
        assert await guard(ctx_admin) == ctx_admin
        assert await guard(ctx_owner) == ctx_owner

    @pytest.mark.asyncio
    async def test_require_tenant_role_denies_insufficient_role(self):
        """require_tenant_role must raise PermissionDeniedError for lower role levels."""
        guard = require_tenant_role(TenantRole.ADMIN)
        ctx_viewer = TenantContext(role=TenantRole.VIEWER.value)
        ctx_analyst = TenantContext(role=TenantRole.SECURITY_ANALYST.value)

        with pytest.raises(PermissionDeniedError, match="Insufficient tenant role"):
            await guard(ctx_viewer)

        with pytest.raises(PermissionDeniedError, match="Insufficient tenant role"):
            await guard(ctx_analyst)

    @pytest.mark.asyncio
    async def test_require_tenant_role_permits_system_admin_override(self):
        """System admin must bypass tenant role restrictions."""
        guard = require_tenant_role(TenantRole.OWNER)
        ctx_sysadmin = TenantContext(role=TenantRole.VIEWER.value, is_system_admin=True)
        res = await guard(ctx_sysadmin)
        assert res.is_system_admin is True
