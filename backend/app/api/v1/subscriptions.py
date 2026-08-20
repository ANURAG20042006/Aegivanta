from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, require_tenant_role, TenantContext
from backend.app.models.tenant import TenantRole
from backend.app.models.subscription import PlanTier
from backend.app.services.subscription_service import SubscriptionService, PLAN_DEFAULTS
from backend.app.services.usage_metering_service import UsageMeteringService
from backend.app.services.billing_provider import get_billing_provider
from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions & Billing"])


class SubscriptionResponse(BaseModel):
    organization_id: str
    plan_tier: str
    status: str
    seat_limit: int
    telemetry_limit_gb_monthly: int
    current_period_start: datetime
    current_period_end: datetime
    features: List[str]


class UpgradePlanRequest(BaseModel):
    new_plan_tier: str


class CheckoutSessionRequest(BaseModel):
    plan_tier: str
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    session_id: str
    url: str


@router.get("/current", response_model=SubscriptionResponse, summary="Get Current Subscription Plan Details")
async def get_current_subscription(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Returns active subscription tier, limits, and entitled feature flags for the organization."""
    if not context.organization_id:
        raise SentinelAIException(status_code=400, detail="Active organization required.")

    sub = await SubscriptionService.get_active_subscription(db, context.organization_id)
    if not sub:
        sub = await SubscriptionService.create_default_subscription(db, context.organization_id, PlanTier.FREE)
        await db.commit()

    plan_meta = PLAN_DEFAULTS.get(sub.plan_tier, PLAN_DEFAULTS[PlanTier.FREE.value])
    return SubscriptionResponse(
        organization_id=sub.organization_id,
        plan_tier=sub.plan_tier,
        status=sub.status,
        seat_limit=sub.seat_limit,
        telemetry_limit_gb_monthly=sub.telemetry_limit_gb_monthly,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        features=plan_meta.get("features", [])
    )


@router.get("/usage", summary="Get Monthly Usage vs Plan Limits")
async def get_subscription_usage(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Returns aggregated usage statistics for current billing period."""
    if not context.tenant_id:
        return {"usage": {}}

    usage_map = await UsageMeteringService.get_monthly_usage_summary(db, context.tenant_id)
    sub = await SubscriptionService.get_active_subscription(db, context.organization_id or "default-org")
    tier_name = sub.plan_tier if sub else "FREE"
    defaults = PLAN_DEFAULTS.get(tier_name, PLAN_DEFAULTS["FREE"])

    return {
        "tenant_id": context.tenant_id,
        "plan_tier": tier_name,
        "limits": {
            "telemetry_gb": defaults["telemetry_limit_gb_monthly"],
            "max_seats": defaults["seat_limit"],
            "max_sensors": defaults["max_sensors"]
        },
        "current_usage": usage_map
    }


@router.post("/upgrade", response_model=SubscriptionResponse, summary="Upgrade Subscription Plan")
async def upgrade_subscription_plan(
    payload: UpgradePlanRequest,
    context: TenantContext = Depends(require_tenant_role(TenantRole.BILLING_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Directly upgrades plan tier and provisions matching feature entitlements."""
    if not context.organization_id:
        raise SentinelAIException(status_code=400, detail="Active organization required.")

    try:
        tier_enum = PlanTier(payload.new_plan_tier.upper())
    except ValueError:
        raise SentinelAIException(status_code=400, detail=f"Invalid plan tier '{payload.new_plan_tier}'.")

    updated_sub = await SubscriptionService.upgrade_plan(db, context.organization_id, tier_enum)

    await ImmutableAuditService.record(
        db=db,
        event_type=AuditEventType.CONFIG_CHANGED,
        actor_id=context.user_id or "system",
        resource=f"org:{context.organization_id}:subscription",
        action=f"Upgraded subscription plan to '{tier_enum.value}'"
    )

    await db.commit()
    plan_meta = PLAN_DEFAULTS.get(updated_sub.plan_tier, PLAN_DEFAULTS[PlanTier.FREE.value])
    return SubscriptionResponse(
        organization_id=updated_sub.organization_id,
        plan_tier=updated_sub.plan_tier,
        status=updated_sub.status,
        seat_limit=updated_sub.seat_limit,
        telemetry_limit_gb_monthly=updated_sub.telemetry_limit_gb_monthly,
        current_period_start=updated_sub.current_period_start,
        current_period_end=updated_sub.current_period_end,
        features=plan_meta.get("features", [])
    )


@router.post("/checkout-session", response_model=CheckoutSessionResponse, summary="Create Billing Checkout Session")
async def create_checkout_session(
    payload: CheckoutSessionRequest,
    context: TenantContext = Depends(require_tenant_role(TenantRole.BILLING_ADMIN))
):
    """Generates a checkout URL for commercial subscription payments."""
    if not context.organization_id:
        raise SentinelAIException(status_code=400, detail="Active organization required.")

    tier_enum = PlanTier(payload.plan_tier.upper())
    provider = get_billing_provider()
    session_data = await provider.create_checkout_session(
        organization_id=context.organization_id,
        plan_tier=tier_enum,
        success_url=payload.success_url,
        cancel_url=payload.cancel_url
    )
    return CheckoutSessionResponse(
        session_id=session_data["session_id"],
        url=session_data["url"]
    )
