import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.tenant import Tenant, TenantMembership
from backend.app.models.identity import IdentityProvider, MFAEnrollment
from backend.app.models.api_key import ApiKey
from backend.app.models.sensor import Sensor
from backend.app.models.integration import CustomerIntegration
from backend.app.models.security_policy import SecurityPolicy

logger = logging.getLogger("SentinelAI.Posture")


class SecurityPostureService:
    """Calculates an explainable, data-driven 0–100 enterprise Security Posture Score."""

    @classmethod
    async def calculate_posture(
        cls,
        db: AsyncSession,
        organization_id: str
    ) -> Dict[str, Any]:
        """Evaluates 5 security dimensions and produces an aggregate 0-100 score."""
        # 1. Identity & MFA Score (Weight: 25%)
        stmt_members = select(TenantMembership).where(TenantMembership.organization_id == organization_id)
        res_members = await db.execute(stmt_members)
        members = res_members.scalars().all()
        total_members = len(members)

        stmt_mfa = select(MFAEnrollment).join(
            TenantMembership, TenantMembership.user_id == MFAEnrollment.user_id
        ).where(
            and_(
                TenantMembership.organization_id == organization_id,
                MFAEnrollment.is_verified == True
            )
        )
        res_mfa = await db.execute(stmt_mfa)
        mfa_count = len(res_mfa.scalars().all())

        mfa_ratio = (mfa_count / total_members) if total_members > 0 else 1.0
        identity_score = int(mfa_ratio * 70) + 30  # Base 30 + up to 70 based on MFA

        # Check SSO
        stmt_sso = select(IdentityProvider).where(
            and_(
                IdentityProvider.organization_id == organization_id,
                IdentityProvider.is_active == True
            )
        )
        res_sso = await db.execute(stmt_sso)
        sso_active = res_sso.scalar_one_or_none() is not None
        if sso_active:
            identity_score = min(100, identity_score + 15)

        # 2. API Security Score (Weight: 20%)
        stmt_keys = select(ApiKey).join(Tenant, Tenant.id == ApiKey.tenant_id).where(
            Tenant.organization_id == organization_id
        )
        res_keys = await db.execute(stmt_keys)
        keys = res_keys.scalars().all()
        if not keys:
            api_score = 90
        else:
            expiring_keys = [k for k in keys if k.expires_at is not None]
            api_score = int((len(expiring_keys) / len(keys)) * 40) + 60

        # 3. Sensor Fleet Health Score (Weight: 20%)
        stmt_sensors = select(Sensor).join(Tenant, Tenant.id == Sensor.tenant_id).where(
            Tenant.organization_id == organization_id
        )
        res_sensors = await db.execute(stmt_sensors)
        sensors = res_sensors.scalars().all()
        if not sensors:
            sensor_score = 85
        else:
            online_sensors = [s for s in sensors if s.status == "ONLINE"]
            sensor_score = int((len(online_sensors) / len(sensors)) * 100)

        # 4. Integration Security Score (Weight: 15%)
        stmt_integ = select(CustomerIntegration).where(CustomerIntegration.organization_id == organization_id)
        res_integ = await db.execute(stmt_integ)
        integrations = res_integ.scalars().all()
        if not integrations:
            integration_score = 85
        else:
            active_integs = [i for i in integrations if i.status == "ACTIVE"]
            integration_score = int((len(active_integs) / len(integrations)) * 100)

        # 5. Security Policies Score (Weight: 20%)
        stmt_policy = select(SecurityPolicy).where(SecurityPolicy.organization_id == organization_id)
        res_policy = await db.execute(stmt_policy)
        policy = res_policy.scalar_one_or_none()

        policy_score = 70
        if policy:
            if policy.require_mfa:
                policy_score += 10
            if policy.require_sso:
                policy_score += 10
            if policy.ip_allowlist:
                policy_score += 10
        policy_score = min(100, policy_score)

        # Aggregate Weighted Score
        overall_score = int(
            (identity_score * 0.25) +
            (api_score * 0.20) +
            (sensor_score * 0.20) +
            (integration_score * 0.15) +
            (policy_score * 0.20)
        )

        recommendations = []
        if mfa_ratio < 1.0:
            recommendations.append("Enforce MFA across all security analyst and administrator accounts.")
        if not sso_active:
            recommendations.append("Configure an Enterprise SSO Identity Provider (OIDC / SAML 2.0).")
        if any(k.expires_at is None for k in keys):
            recommendations.append("Set expiration policies on long-lived customer API keys.")
        if any(s.status != "ONLINE" for s in sensors):
            recommendations.append("Investigate offline telemetry sensors in your agent fleet.")

        return {
            "organization_id": organization_id,
            "overall_posture_score": overall_score,
            "rating": "STRONG" if overall_score >= 85 else "MODERATE" if overall_score >= 70 else "NEEDS_ATTENTION",
            "dimension_scores": {
                "identity_security": identity_score,
                "api_security": api_score,
                "sensor_security": sensor_score,
                "integration_security": integration_score,
                "policy_compliance": policy_score
            },
            "metrics": {
                "mfa_adoption_pct": round(mfa_ratio * 100, 1),
                "sso_enabled": sso_active,
                "active_sensors_count": len([s for s in sensors if s.status == "ONLINE"]),
                "total_sensors_count": len(sensors)
            },
            "recommendations": recommendations,
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
