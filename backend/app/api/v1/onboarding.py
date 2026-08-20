from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.dependencies import get_current_user
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.models.user import User
from backend.app.models.tenant import Organization, Tenant, TenantMembership
from backend.app.models.sensor import Sensor
from backend.app.models.alert import Alert

router = APIRouter(prefix="/onboarding", tags=["Customer Onboarding"])


class OnboardingStatusResponse(BaseModel):
    has_organization: bool
    organization_name: Optional[str] = None
    organization_slug: Optional[str] = None
    has_tenant: bool
    tenant_name: Optional[str] = None
    has_sensor: bool
    sensor_count: int
    has_telemetry: bool
    current_step: int  # 1: Org, 2: Plan/Tenant, 3: Sensor/API Key, 4: Ready
    completed: bool


@router.get("/status", response_model=OnboardingStatusResponse, summary="Get Customer Onboarding Progress")
async def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates guided onboarding progress across organization setup, plan selection, and sensor deployment."""
    has_org = False
    org_name = None
    org_slug = None
    has_tenant = False
    tenant_name = None
    sensor_count = 0
    has_telemetry = False

    if context.organization_id:
        stmt_org = select(Organization).where(Organization.id == context.organization_id)
        res_org = await db.execute(stmt_org)
        org = res_org.scalar_one_or_none()
        if org:
            has_org = True
            org_name = org.name
            org_slug = org.slug

    if context.tenant_id:
        stmt_ten = select(Tenant).where(Tenant.id == context.tenant_id)
        res_ten = await db.execute(stmt_ten)
        ten = res_ten.scalar_one_or_none()
        if ten:
            has_tenant = True
            tenant_name = ten.name

        # Check sensors
        stmt_sen = select(Sensor).where(Sensor.tenant_id == context.tenant_id)
        res_sen = await db.execute(stmt_sen)
        sensors = res_sen.scalars().all()
        sensor_count = len(sensors)

        # Check telemetry / alerts
        stmt_alt = select(Alert).limit(1)
        res_alt = await db.execute(stmt_alt)
        has_telemetry = res_alt.scalar_one_or_none() is not None

    current_step = 1
    if not has_org:
        current_step = 1
    elif not has_tenant:
        current_step = 2
    elif sensor_count == 0:
        current_step = 3
    else:
        current_step = 4

    completed = (current_step == 4 and (has_telemetry or sensor_count > 0))

    return OnboardingStatusResponse(
        has_organization=has_org,
        organization_name=org_name,
        organization_slug=org_slug,
        has_tenant=has_tenant,
        tenant_name=tenant_name,
        has_sensor=(sensor_count > 0),
        sensor_count=sensor_count,
        has_telemetry=has_telemetry,
        current_step=current_step,
        completed=completed
    )
