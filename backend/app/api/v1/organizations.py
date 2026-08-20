from typing import List, Optional
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user
from backend.app.core.tenant import resolve_tenant_context, require_tenant_role, TenantContext
from backend.app.models.user import User
from backend.app.models.tenant import Organization, Tenant, TenantMembership, TenantRole, TenantSettings
from backend.app.models.subscription import PlanTier
from backend.app.services.subscription_service import SubscriptionService
from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType
from backend.app.core.exceptions import SentinelAIException, PermissionDeniedError

router = APIRouter(prefix="/organizations", tags=["Organizations"])


class CreateOrgRequest(BaseModel):
    name: str
    slug: str
    billing_email: EmailStr
    plan_tier: Optional[str] = "FREE"


class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: str = "SECURITY_ANALYST"
    tenant_id: Optional[str] = None


class UpdateMemberRoleRequest(BaseModel):
    role: str


class OrgResponse(BaseModel):
    id: str
    name: str
    slug: str
    billing_email: str
    plan_tier: str
    status: str

    class Config:
        from_attributes = True


class MemberResponse(BaseModel):
    id: str
    user_id: str
    username: Optional[str] = None
    email: Optional[str] = None
    role: str
    status: str

    class Config:
        from_attributes = True


@router.post("", response_model=OrgResponse, status_code=status.HTTP_201_CREATED, summary="Create New Customer Organization")
async def create_organization(
    payload: CreateOrgRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new top-level organization, a default workspace tenant, and grants OWNER role to creator."""
    stmt = select(Organization).where(Organization.slug == payload.slug)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise SentinelAIException(status_code=400, detail=f"Organization with slug '{payload.slug}' already exists.")

    plan_enum = PlanTier.FREE
    try:
        plan_enum = PlanTier(payload.plan_tier.upper())
    except Exception:
        pass

    org = Organization(
        name=payload.name,
        slug=payload.slug,
        billing_email=str(payload.billing_email),
        plan_tier=plan_enum.value,
        status="ACTIVE"
    )
    db.add(org)
    await db.flush()

    # Create default tenant
    tenant = Tenant(
        organization_id=org.id,
        name=f"{payload.name} (Production)",
        slug="production",
        environment_type="production"
    )
    db.add(tenant)
    await db.flush()

    # Create tenant settings
    settings = TenantSettings(tenant_id=tenant.id)
    db.add(settings)

    # Assign OWNER membership to current user
    membership = TenantMembership(
        user_id=current_user.id,
        organization_id=org.id,
        tenant_id=tenant.id,
        role=TenantRole.OWNER.value,
        status="ACTIVE"
    )
    db.add(membership)

    # Create subscription
    await SubscriptionService.create_default_subscription(db, org.id, plan_enum)

    # Immutable Audit
    await ImmutableAuditService.record(
        db=db,
        event_type=AuditEventType.ORGANIZATION_CREATED if hasattr(AuditEventType, "ORGANIZATION_CREATED") else AuditEventType.CONFIG_CHANGED,
        actor_id=current_user.id,
        resource=f"org:{org.id}",
        action=f"Created organization '{org.name}' ({org.slug})"
    )

    await db.commit()
    return org


@router.get("/me", response_model=List[OrgResponse], summary="List My Organizations")
async def list_my_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns all organizations the current authenticated user belongs to."""
    stmt = (
        select(Organization)
        .join(TenantMembership, TenantMembership.organization_id == Organization.id)
        .where(TenantMembership.user_id == current_user.id)
        .distinct()
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.get("/{org_id}/members", response_model=List[MemberResponse], summary="List Organization Members")
async def list_members(
    org_id: str,
    context: TenantContext = Depends(require_tenant_role(TenantRole.SECURITY_ANALYST)),
    db: AsyncSession = Depends(get_db)
):
    """Lists all member accounts in the organization."""
    stmt = select(TenantMembership, User).join(User, User.id == TenantMembership.user_id).where(
        TenantMembership.organization_id == org_id
    )
    res = await db.execute(stmt)
    rows = res.all()

    members = []
    for membership, user in rows:
        members.append(MemberResponse(
            id=membership.id,
            user_id=user.id,
            username=user.username,
            email=user.email,
            role=membership.role,
            status=membership.status
        ))
    return members


@router.post("/{org_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED, summary="Invite or Add Member to Organization")
async def invite_member(
    org_id: str,
    payload: InviteMemberRequest,
    context: TenantContext = Depends(require_tenant_role(TenantRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Invites or adds a user to the organization by email."""
    stmt_user = select(User).where(User.email == payload.email)
    res_user = await db.execute(stmt_user)
    user = res_user.scalar_one_or_none()
    if not user:
        raise SentinelAIException(status_code=404, detail=f"User with email '{payload.email}' not found. User must register first.")

    # Check if already a member
    stmt_mem = select(TenantMembership).where(
        and_(
            TenantMembership.organization_id == org_id,
            TenantMembership.user_id == user.id
        )
    )
    res_mem = await db.execute(stmt_mem)
    if res_mem.scalar_one_or_none():
        raise SentinelAIException(status_code=400, detail="User is already a member of this organization.")

    role_val = payload.role.upper()
    if role_val not in [r.value for r in TenantRole]:
        role_val = TenantRole.SECURITY_ANALYST.value

    membership = TenantMembership(
        user_id=user.id,
        organization_id=org_id,
        tenant_id=payload.tenant_id,
        role=role_val,
        status="ACTIVE"
    )
    db.add(membership)

    await ImmutableAuditService.record(
        db=db,
        event_type=AuditEventType.USER_ROLE_CHANGED,
        actor_id=context.user_id or "system",
        resource=f"org:{org_id}:user:{user.id}",
        action=f"Added member '{user.email}' with role '{role_val}'"
    )

    await db.commit()
    return MemberResponse(
        id=membership.id,
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=membership.role,
        status=membership.status
    )
