from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, require_tenant_role, TenantContext
from backend.app.models.tenant import Tenant, TenantSettings, TenantRole
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/tenants", tags=["Tenants"])


class CreateTenantRequest(BaseModel):
    name: str
    slug: str
    environment_type: Optional[str] = "production"


class TenantResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    slug: str
    environment_type: str
    is_active: bool

    class Config:
        from_attributes = True


class TenantSettingsResponse(BaseModel):
    id: str
    tenant_id: str
    retention_days_hot: int
    retention_days_warm: int
    retention_days_cold: int
    require_mfa: bool
    notification_webhook_url: Optional[str] = None

    class Config:
        from_attributes = True


class UpdateTenantSettingsRequest(BaseModel):
    retention_days_hot: Optional[int] = None
    retention_days_warm: Optional[int] = None
    retention_days_cold: Optional[int] = None
    require_mfa: Optional[bool] = None
    notification_webhook_url: Optional[str] = None


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED, summary="Create Workspace Tenant")
async def create_tenant(
    payload: CreateTenantRequest,
    context: TenantContext = Depends(require_tenant_role(TenantRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new workspace tenant within current organization."""
    if not context.organization_id:
        raise SentinelAIException(status_code=400, detail="Active organization context required.")

    tenant = Tenant(
        organization_id=context.organization_id,
        name=payload.name,
        slug=payload.slug,
        environment_type=payload.environment_type or "production"
    )
    db.add(tenant)
    await db.flush()

    settings = TenantSettings(tenant_id=tenant.id)
    db.add(settings)
    await db.commit()
    await db.refresh(tenant)
    return tenant


@router.get("", response_model=List[TenantResponse], summary="List Organization Tenants")
async def list_tenants(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists all tenant workspaces in current organization."""
    if not context.organization_id:
        return []
    stmt = select(Tenant).where(Tenant.organization_id == context.organization_id)
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.get("/{tenant_id}/settings", response_model=TenantSettingsResponse, summary="Get Tenant Settings")
async def get_tenant_settings(
    tenant_id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Fetches tenant settings including data retention and MFA configuration."""
    stmt = select(TenantSettings).where(TenantSettings.tenant_id == tenant_id)
    res = await db.execute(stmt)
    settings = res.scalar_one_or_none()
    if not settings:
        settings = TenantSettings(tenant_id=tenant_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.put("/{tenant_id}/settings", response_model=TenantSettingsResponse, summary="Update Tenant Settings")
async def update_tenant_settings(
    tenant_id: str,
    payload: UpdateTenantSettingsRequest,
    context: TenantContext = Depends(require_tenant_role(TenantRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Updates tenant compliance, data retention, and security parameters."""
    stmt = select(TenantSettings).where(TenantSettings.tenant_id == tenant_id)
    res = await db.execute(stmt)
    settings = res.scalar_one_or_none()
    if not settings:
        settings = TenantSettings(tenant_id=tenant_id)
        db.add(settings)

    if payload.retention_days_hot is not None:
        settings.retention_days_hot = payload.retention_days_hot
    if payload.retention_days_warm is not None:
        settings.retention_days_warm = payload.retention_days_warm
    if payload.retention_days_cold is not None:
        settings.retention_days_cold = payload.retention_days_cold
    if payload.require_mfa is not None:
        settings.require_mfa = payload.require_mfa
    if payload.notification_webhook_url is not None:
        settings.notification_webhook_url = payload.notification_webhook_url

    await db.commit()
    await db.refresh(settings)
    return settings
