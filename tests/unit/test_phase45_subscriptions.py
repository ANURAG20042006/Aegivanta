"""
tests/unit/test_phase45_subscriptions.py
========================================
Phase 4.5 & 4.6 Subscriptions & Feature Entitlement Tests.
Validates plan defaults, feature flag enforcement, and plan upgrade logic.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.models.subscription import PlanTier
from backend.app.services.subscription_service import SubscriptionService, PLAN_DEFAULTS
from backend.app.services.feature_entitlement_service import (
    FeatureEntitlementService,
    FeatureKeys,
    require_feature
)
from backend.app.core.tenant import TenantContext
from backend.app.core.exceptions import PermissionDeniedError


class TestSubscriptionsAndEntitlements:

    def test_plan_tier_definitions_exist(self):
        """All required commercial tiers (FREE, PROFESSIONAL, BUSINESS, ENTERPRISE) must be defined."""
        tiers = [PlanTier.FREE.value, PlanTier.PROFESSIONAL.value, PlanTier.BUSINESS.value, PlanTier.ENTERPRISE.value]
        for t in tiers:
            assert t in PLAN_DEFAULTS
            assert "seat_limit" in PLAN_DEFAULTS[t]
            assert "telemetry_limit_gb_monthly" in PLAN_DEFAULTS[t]
            assert "features" in PLAN_DEFAULTS[t]

    def test_enterprise_tier_contains_all_advanced_features(self):
        """ENTERPRISE plan must include all advanced security capabilities."""
        ent_features = PLAN_DEFAULTS[PlanTier.ENTERPRISE.value]["features"]
        required = [
            FeatureKeys.THREAT_HUNTING,
            FeatureKeys.SOAR,
            FeatureKeys.ADVANCED_AI,
            FeatureKeys.ATTACK_GRAPH,
            FeatureKeys.API_ACCESS,
            FeatureKeys.SSO,
            FeatureKeys.LONG_TERM_RETENTION
        ]
        for f in required:
            assert f in ent_features, f"Missing feature in ENTERPRISE tier: {f}"

    @pytest.mark.asyncio
    async def test_require_feature_permits_entitled_tenant(self):
        """require_feature must permit access when is_entitled returns True."""
        db = AsyncMock()
        guard = require_feature(FeatureKeys.THREAT_HUNTING)
        ctx = TenantContext(organization_id="org-123")

        # Mock is_entitled to True
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(FeatureEntitlementService, "is_entitled", AsyncMock(return_value=True))
            res = await guard(context=ctx, db=db)
            assert res == ctx

    @pytest.mark.asyncio
    async def test_require_feature_denies_unentitled_tenant(self):
        """require_feature must raise PermissionDeniedError when plan lacks feature."""
        db = AsyncMock()
        guard = require_feature(FeatureKeys.SOAR)
        ctx = TenantContext(organization_id="org-free")

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(FeatureEntitlementService, "is_entitled", AsyncMock(return_value=False))
            with pytest.raises(PermissionDeniedError, match="not entitled to feature"):
                await guard(context=ctx, db=db)
