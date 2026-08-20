import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.subscription import Subscription, PlanTier, FeatureEntitlement
from backend.app.models.tenant import Organization
from backend.app.core.exceptions import SentinelAIException

logger = logging.getLogger("SentinelAI.Subscription")

PLAN_DEFAULTS: Dict[str, Dict[str, Any]] = {
    PlanTier.FREE.value: {
        "seat_limit": 3,
        "telemetry_limit_gb_monthly": 5,
        "retention_days": 7,
        "max_sensors": 2,
        "price_monthly_usd": 0.0,
        "features": [
            "FEATURE_BASIC_DETECTION",
            "FEATURE_ALERTS",
            "FEATURE_DASHBOARD"
        ]
    },
    PlanTier.PROFESSIONAL.value: {
        "seat_limit": 10,
        "telemetry_limit_gb_monthly": 50,
        "retention_days": 30,
        "max_sensors": 25,
        "price_monthly_usd": 499.0,
        "features": [
            "FEATURE_BASIC_DETECTION",
            "FEATURE_ALERTS",
            "FEATURE_DASHBOARD",
            "FEATURE_THREAT_INTEL",
            "FEATURE_ATTACK_GRAPH",
            "FEATURE_INVESTIGATIONS",
            "FEATURE_ANALYTICS"
        ]
    },
    PlanTier.BUSINESS.value: {
        "seat_limit": 25,
        "telemetry_limit_gb_monthly": 250,
        "retention_days": 90,
        "max_sensors": 100,
        "price_monthly_usd": 1499.0,
        "features": [
            "FEATURE_BASIC_DETECTION",
            "FEATURE_ALERTS",
            "FEATURE_DASHBOARD",
            "FEATURE_THREAT_INTEL",
            "FEATURE_ATTACK_GRAPH",
            "FEATURE_INVESTIGATIONS",
            "FEATURE_ANALYTICS",
            "FEATURE_THREAT_HUNTING",
            "FEATURE_SOAR",
            "FEATURE_API_ACCESS",
            "FEATURE_CUSTOM_RULES",
            "FEATURE_INTEGRATIONS"
        ]
    },
    PlanTier.ENTERPRISE.value: {
        "seat_limit": 9999,
        "telemetry_limit_gb_monthly": 5000,
        "retention_days": 365,
        "max_sensors": 9999,
        "price_monthly_usd": 4999.0,
        "features": [
            "FEATURE_BASIC_DETECTION",
            "FEATURE_ALERTS",
            "FEATURE_DASHBOARD",
            "FEATURE_THREAT_INTEL",
            "FEATURE_ATTACK_GRAPH",
            "FEATURE_INVESTIGATIONS",
            "FEATURE_ANALYTICS",
            "FEATURE_THREAT_HUNTING",
            "FEATURE_SOAR",
            "FEATURE_ADVANCED_AI",
            "FEATURE_API_ACCESS",
            "FEATURE_CUSTOM_RULES",
            "FEATURE_INTEGRATIONS",
            "FEATURE_SSO",
            "FEATURE_LONG_TERM_RETENTION",
            "FEATURE_DEDICATED_WORKER",
            "FEATURE_COMPLIANCE_EXPORT"
        ]
    }
}


class SubscriptionService:
    """Manages organization subscriptions, renewals, plan upgrades, and tier definitions."""

    @classmethod
    async def create_default_subscription(
        cls,
        db: AsyncSession,
        organization_id: str,
        plan_tier: PlanTier = PlanTier.FREE
    ) -> Subscription:
        """Initializes a new subscription for an organization."""
        defaults = PLAN_DEFAULTS.get(plan_tier.value, PLAN_DEFAULTS[PlanTier.FREE.value])
        now = datetime.now(timezone.utc)
        period_end = now + timedelta(days=30)

        sub = Subscription(
            organization_id=organization_id,
            plan_tier=plan_tier.value,
            status="ACTIVE",
            current_period_start=now,
            current_period_end=period_end,
            seat_limit=defaults["seat_limit"],
            telemetry_limit_gb_monthly=defaults["telemetry_limit_gb_monthly"]
        )
        db.add(sub)
        await db.flush()

        # Provision base feature entitlements
        for feat in defaults["features"]:
            entitlement = FeatureEntitlement(
                organization_id=organization_id,
                feature_key=feat,
                is_enabled=True
            )
            db.add(entitlement)

        await db.flush()
        return sub

    @classmethod
    async def get_active_subscription(
        cls,
        db: AsyncSession,
        organization_id: str
    ) -> Optional[Subscription]:
        """Fetches current active subscription for organization."""
        stmt = select(Subscription).where(
            and_(
                Subscription.organization_id == organization_id,
                Subscription.status == "ACTIVE"
            )
        ).order_by(Subscription.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def upgrade_plan(
        cls,
        db: AsyncSession,
        organization_id: str,
        new_plan_tier: PlanTier
    ) -> Subscription:
        """Upgrades organization subscription to higher tier and syncs entitlements."""
        stmt = select(Organization).where(Organization.id == organization_id)
        res = await db.execute(stmt)
        org = res.scalar_one_or_none()
        if not org:
            raise SentinelAIException(status_code=404, detail="Organization not found")

        sub = await cls.get_active_subscription(db, organization_id)
        defaults = PLAN_DEFAULTS.get(new_plan_tier.value, PLAN_DEFAULTS[PlanTier.FREE.value])

        if sub:
            sub.plan_tier = new_plan_tier.value
            sub.seat_limit = defaults["seat_limit"]
            sub.telemetry_limit_gb_monthly = defaults["telemetry_limit_gb_monthly"]
            sub.updated_at = datetime.now(timezone.utc)
        else:
            sub = await cls.create_default_subscription(db, organization_id, new_plan_tier)

        org.plan_tier = new_plan_tier.value
        org.updated_at = datetime.now(timezone.utc)

        # Update entitlements
        for feat in defaults["features"]:
            stmt_feat = select(FeatureEntitlement).where(
                and_(
                    FeatureEntitlement.organization_id == organization_id,
                    FeatureEntitlement.feature_key == feat
                )
            )
            res_feat = await db.execute(stmt_feat)
            existing = res_feat.scalar_one_or_none()
            if not existing:
                db.add(FeatureEntitlement(
                    organization_id=organization_id,
                    feature_key=feat,
                    is_enabled=True
                ))
            else:
                existing.is_enabled = True

        await db.flush()
        return sub
