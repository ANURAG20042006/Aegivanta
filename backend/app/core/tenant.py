import logging
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Optional, List, Set, Callable
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.tenant import Organization, Tenant, TenantMembership, TenantRole
from backend.app.core.exceptions import AuthenticationError, PermissionDeniedError, SentinelAIException

logger = logging.getLogger("SentinelAI.Tenant")

# Context variable for request-scoped tenant isolation
_tenant_context_var: ContextVar[Optional["TenantContext"]] = ContextVar("tenant_context", default=None)


@dataclass
class TenantContext:
    """Security boundary context associated with the active request."""
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    tenant_id: Optional[str] = None
    role: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    is_system_admin: bool = False
    is_api_key_auth: bool = False
    api_key_id: Optional[str] = None


def get_tenant_context() -> Optional[TenantContext]:
    """Retrieves current request tenant context."""
    return _tenant_context_var.get()


def set_tenant_context(context: TenantContext) -> None:
    """Sets current request tenant context."""
    _tenant_context_var.set(context)


# Canonical hierarchy for Tenant Roles
TENANT_ROLE_HIERARCHY = {
    TenantRole.OWNER.value: 100,
    TenantRole.ADMIN.value: 80,
    TenantRole.SECURITY_ANALYST.value: 60,
    TenantRole.RESPONDER.value: 50,
    TenantRole.API_ADMIN.value: 40,
    TenantRole.BILLING_ADMIN.value: 30,
    TenantRole.VIEWER.value: 10,
}


async def resolve_tenant_context(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TenantContext:
    """
    Resolves authoritative TenantContext for an authenticated User.
    Inspects optional X-Tenant-ID header but strictly validates that the user is an active member
    of the requested tenant. Never trusts client-supplied tenant ID blindly.
    """
    requested_tenant_id = request.headers.get("X-Tenant-ID", "").strip() or request.query_params.get("tenant_id", "").strip()

    # Query user's memberships
    stmt = select(TenantMembership).where(
        and_(
            TenantMembership.user_id == current_user.id,
            TenantMembership.status == "ACTIVE"
        )
    )
    result = await db.execute(stmt)
    memberships = result.scalars().all()

    # System-level administrator fallback for legacy/maintenance
    if current_user.role.lower() in ["admin", "root"] and not memberships:
        # Create default context for backward compatibility
        context = TenantContext(
            user_id=current_user.id,
            organization_id="default-org",
            tenant_id="default-tenant",
            role=TenantRole.OWNER.value,
            is_system_admin=True
        )
        set_tenant_context(context)
        return context

    if not memberships:
        # If user has no memberships yet (e.g. freshly registered viewer), default safe viewer context
        context = TenantContext(
            user_id=current_user.id,
            organization_id=None,
            tenant_id=None,
            role=TenantRole.VIEWER.value,
            is_system_admin=(current_user.role.lower() in ["admin", "root"])
        )
        set_tenant_context(context)
        return context

    # If a specific tenant was requested, ensure user is a member
    active_membership = None
    if requested_tenant_id:
        for m in memberships:
            if m.tenant_id == requested_tenant_id or m.organization_id == requested_tenant_id:
                active_membership = m
                break
        if not active_membership and current_user.role.lower() not in ["admin", "root"]:
            raise PermissionDeniedError(detail=f"Access denied to tenant '{requested_tenant_id}'. User is not an active member.")
    
    if not active_membership:
        active_membership = memberships[0]

    context = TenantContext(
        user_id=current_user.id,
        organization_id=active_membership.organization_id,
        tenant_id=active_membership.tenant_id or active_membership.organization_id,
        role=active_membership.role,
        is_system_admin=(current_user.role.lower() in ["admin", "root"])
    )
    set_tenant_context(context)
    return context


def require_tenant_role(min_role: TenantRole) -> Callable:
    """Dependency factory ensuring current user has at least the specified tenant role level."""
    min_level = TENANT_ROLE_HIERARCHY.get(min_role.value, 0)

    async def role_guard(context: TenantContext = Depends(resolve_tenant_context)) -> TenantContext:
        if context.is_system_admin:
            return context
        user_level = TENANT_ROLE_HIERARCHY.get(context.role or "", 0)
        if user_level < min_level:
            raise PermissionDeniedError(
                detail=f"Insufficient tenant role. Required: '{min_role.value}', user has: '{context.role}'"
            )
        return context

    return role_guard
