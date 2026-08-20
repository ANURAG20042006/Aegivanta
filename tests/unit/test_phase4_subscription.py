"""
tests/unit/test_phase4_subscription.py
======================================
Unit tests for Phase 4 Subscriptions & Feature Entitlements.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.models.subscription import PlanTier, Subscription, FeatureEntitlement
from backend.app.services.subscription_service import SubscriptionService, PLAN_DEFAULTS
from backend.app.services.feature_entitlement_service import FeatureEntitlementService, FeatureKeys


def test_plan_defaults_consistency():
    """Validates quota ceilings across all four commercial tiers."""
    free_plan = PLAN_DEFAULTS[PlanTier.FREE.value]
    pro_plan = PLAN_DEFAULTS[PlanTier.PROFESSIONAL.value]
    biz_plan = PLAN_DEFAULTS[PlanTier.BUSINESS.value]
    ent_plan = PLAN_DEFAULTS[PlanTier.ENTERPRISE.value]

    assert free_plan["seat_limit"] < pro_plan["seat_limit"]
    assert pro_plan["seat_limit"] < biz_plan["seat_limit"]
    assert free_plan["telemetry_limit_gb_monthly"] < pro_plan["telemetry_limit_gb_monthly"]
    assert pro_plan["telemetry_limit_gb_monthly"] < biz_plan["telemetry_limit_gb_monthly"]
    assert biz_plan["telemetry_limit_gb_monthly"] < ent_plan["telemetry_limit_gb_monthly"]


@pytest.mark.asyncio
async def test_entitlement_service_system_admin_bypass():
    """System default organization always has full capability entitlements."""
    db = AsyncMock()
    has_hunting = await FeatureEntitlementService.is_entitled(db, "default-org", FeatureKeys.THREAT_HUNTING)
    has_ai = await FeatureEntitlementService.is_entitled(db, "default-org", FeatureKeys.ADVANCED_AI)

    assert has_hunting is True
    assert has_ai is True
