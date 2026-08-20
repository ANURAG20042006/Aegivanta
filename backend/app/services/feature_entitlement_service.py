import logging
from typing import Callable, List, Optional
from fastapi import Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.models.subscription import FeatureEntitlement
from backend.app.core.exceptions import PermissionDeniedError

logger = logging.getLogger("SentinelAI.Entitlement")


class FeatureKeys:
    BASIC_DETECTION = "FEATURE_BASIC_DETECTION"
    ALERTS = "FEATURE_ALERTS"
    DASHBOARD = "FEATURE_DASHBOARD"
    THREAT_INTEL = "FEATURE_THREAT_INTEL"
    ATTACK_GRAPH = "FEATURE_ATTACK_GRAPH"
    INVESTIGATIONS = "FEATURE_INVESTIGATIONS"
    ANALYTICS = "FEATURE_ANALYTICS"
    THREAT_HUNTING = "FEATURE_THREAT_HUNTING"
    SOAR = "FEATURE_SOAR"
    ADVANCED_AI = "FEATURE_ADVANCED_AI"
    API_ACCESS = "FEATURE_API_ACCESS"
    CUSTOM_RULES = "FEATURE_CUSTOM_RULES"
    INTEGRATIONS = "FEATURE_INTEGRATIONS"
    SSO = "FEATURE_SSO"
    LONG_TERM_RETENTION = "FEATURE_LONG_TERM_RETENTION"
    DEDICATED_WORKER = "FEATURE_DEDICATED_WORKER"
    COMPLIANCE_EXPORT = "FEATURE_COMPLIANCE_EXPORT"


class FeatureEntitlementService:
    """Evaluates whether an organization is entitled to use specific capabilities."""

    @classmethod
    async def is_entitled(
        cls,
        db: AsyncSession,
        organization_id: Optional[str],
        feature_key: str
    ) -> bool:
        """Returns True if the feature is explicitly enabled for the organization."""
        if not organization_id or organization_id == "default-org":
            return True  # System administrator / internal default has full access

        stmt = select(FeatureEntitlement).where(
            and_(
                FeatureEntitlement.organization_id == organization_id,
                FeatureEntitlement.feature_key == feature_key
            )
        )
        res = await db.execute(stmt)
        entitlement = res.scalar_one_or_none()
        if entitlement:
            return entitlement.is_enabled
        return False

    @classmethod
    async def get_all_entitlements(
        cls,
        db: AsyncSession,
        organization_id: Optional[str]
    ) -> List[str]:
        """Returns list of all active feature keys for the organization."""
        if not organization_id or organization_id == "default-org":
            return [getattr(FeatureKeys, k) for k in dir(FeatureKeys) if k.isupper()]

        stmt = select(FeatureEntitlement.feature_key).where(
            and_(
                FeatureEntitlement.organization_id == organization_id,
                FeatureEntitlement.is_enabled == True
            )
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())


def require_feature(feature_key: str) -> Callable:
    """FastAPI dependency that enforces feature entitlement on routes."""
    async def entitlement_checker(
        context: TenantContext = Depends(resolve_tenant_context),
        db: AsyncSession = Depends(get_db)
    ) -> TenantContext:
        if context.is_system_admin:
            return context

        is_allowed = await FeatureEntitlementService.is_entitled(
            db, context.organization_id, feature_key
        )
        if not is_allowed:
            raise PermissionDeniedError(
                detail=f"Organization plan is not entitled to feature '{feature_key}'. Please upgrade subscription."
            )
        return context

    return entitlement_checker
