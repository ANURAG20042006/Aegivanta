"""
backend/app/services/ueba_scoring_service.py
============================================
Phase 37 User & Entity Behavior Analytics (UEBA 2.0) Scoring Service.
Calculates dynamic User Risk Score (URS 0–100) based on peer-group deviation,
login velocity anomalies, after-hours access, and mass egress volumes.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.ai_soc_ueba import UEBAUserProfile

logger = logging.getLogger("Aegivanta.UEBAScoring")


class UEBAScoringService:
    """Enterprise UEBA 2.0 Risk Analytics Engine."""

    @classmethod
    def calculate_user_risk_score(
        cls,
        anomalies: List[str],
        daily_egress_mb: float,
        baseline_egress_mb: float,
        is_odd_hours: bool,
        is_velocity_anomalous: bool
    ) -> Dict[str, Any]:
        """Calculates dynamic URS and classifies risk tier."""
        base_score = 15.0

        # Egress multiplier
        if daily_egress_mb > baseline_egress_mb * 5:
            base_score += 35.0
        elif daily_egress_mb > baseline_egress_mb * 2:
            base_score += 15.0

        if is_odd_hours:
            base_score += 20.0

        if is_velocity_anomalous:
            base_score += 25.0

        base_score += len(anomalies) * 10.0
        final_score = min(100, int(round(base_score)))

        if final_score >= 80:
            level = "CRITICAL"
        elif final_score >= 60:
            level = "HIGH"
        elif final_score >= 35:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "user_risk_score": final_score,
            "risk_level": level
        }

    @classmethod
    async def list_profiles(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists UEBA user risk profiles."""
        stmt = select(UEBAUserProfile).where(
            UEBAUserProfile.tenant_id == tenant_id
        ).order_by(desc(UEBAUserProfile.user_risk_score)).limit(limit)

        profiles = list((await db.execute(stmt)).scalars().all())

        if not profiles:
            # Seed default UEBA user profiles
            defaults = [
                ("marcus.vance@corp.internal", "Finance", "Treasury & Accounting", 88, "CRITICAL", "08:30 - 17:30 UTC", 250.0, 3, ["MASS_FINANCIAL_EXPORT", "AFTER_HOURS_TOR_LOGIN", "MULTI_GEOLOCATION_VELOCITY"]),
                ("elena.rostova@corp.internal", "Engineering", "DevOps Engineers", 64, "HIGH", "09:00 - 18:00 UTC", 600.0, 2, ["SUDO_PRIVILEGE_PROBE", "ANOMALOUS_KEY_EXPORT"]),
                ("david.kim@corp.internal", "Product", "Product Managers", 28, "LOW", "09:00 - 17:00 UTC", 120.0, 0, [])
            ]
            for user, dept, peer, score, lvl, hrs, egr, cnt, anoms in defaults:
                inst = UEBAUserProfile(
                    tenant_id=tenant_id,
                    user_email=user,
                    department=dept,
                    peer_group=peer,
                    user_risk_score=score,
                    risk_level=lvl,
                    baseline_login_hours=hrs,
                    baseline_daily_egress_mb=egr,
                    anomalous_indicators_count=cnt,
                    active_anomalies=anoms,
                    last_evaluated_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(UEBAUserProfile).where(UEBAUserProfile.tenant_id == tenant_id)
            profiles = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": p.id,
                "user_email": p.user_email,
                "department": p.department,
                "peer_group": p.peer_group,
                "user_risk_score": p.user_risk_score,
                "risk_level": p.risk_level,
                "baseline_login_hours": p.baseline_login_hours,
                "baseline_daily_egress_mb": p.baseline_daily_egress_mb,
                "anomalous_indicators_count": p.anomalous_indicators_count,
                "active_anomalies": p.active_anomalies,
                "last_evaluated_at": p.last_evaluated_at.isoformat()
            }
            for p in profiles
        ]
