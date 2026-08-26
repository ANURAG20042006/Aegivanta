"""
backend/app/services/cyber_roi_service.py
==========================================
Phase 47 — Cyber ROI & Financial Risk Quantification service.
Computes and stores quantified security investment return metrics.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.executive_security_intelligence import CyberROIRecord


class CyberROIService:

    @classmethod
    async def list_roi_records(
        cls,
        db: AsyncSession,
        tenant_id: str = "default-tenant",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Lists historical Cyber ROI records. In demo/lab mode, seeds baseline quarters if empty."""
        from backend.app.config import settings
        is_production = (
            getattr(settings, "OPERATING_MODE", "").upper() == "PRODUCTION" or
            getattr(settings, "APP_ENV", "").lower() == "production" or
            getattr(settings, "AEGIVANTA_ENVIRONMENT", "").upper() == "PRODUCTION"
        )
        result = await db.execute(
            select(CyberROIRecord)
            .where(CyberROIRecord.tenant_id == tenant_id)
            .order_by(CyberROIRecord.calculated_at.desc())
            .limit(limit)
        )
        records = result.scalars().all()

        if not records and not is_production:
            await cls._seed_defaults(db, tenant_id)
            result2 = await db.execute(
                select(CyberROIRecord)
                .where(CyberROIRecord.tenant_id == tenant_id)
                .order_by(CyberROIRecord.calculated_at.desc())
                .limit(limit)
            )
            records = result2.scalars().all()

        return [cls._serialize(r) for r in records]

    @classmethod
    async def get_latest_roi(
        cls,
        db: AsyncSession,
        tenant_id: str = "default-tenant"
    ) -> Dict[str, Any]:
        """Returns the most recent Cyber ROI record."""
        from backend.app.config import settings
        is_production = (
            getattr(settings, "OPERATING_MODE", "").upper() == "PRODUCTION" or
            getattr(settings, "APP_ENV", "").lower() == "production" or
            getattr(settings, "AEGIVANTA_ENVIRONMENT", "").upper() == "PRODUCTION"
        )
        result = await db.execute(
            select(CyberROIRecord)
            .where(CyberROIRecord.tenant_id == tenant_id)
            .order_by(CyberROIRecord.calculated_at.desc())
            .limit(1)
        )
        record = result.scalars().first()

        if not record and not is_production:
            await cls._seed_defaults(db, tenant_id)
            result2 = await db.execute(
                select(CyberROIRecord)
                .where(CyberROIRecord.tenant_id == tenant_id)
                .order_by(CyberROIRecord.calculated_at.desc())
                .limit(1)
            )
            record = result2.scalars().first()

        return cls._serialize(record) if record else {
            "status": "NO_DATA",
            "net_annual_cyber_benefit": 0.0,
            "total_roi_percentage": 0.0,
            "annual_investment": 0.0,
            "total_risk_prevented": 0.0,
            "breach_reduction_percentage": 0.0
        }


    @classmethod
    async def _seed_defaults(cls, db: AsyncSession, tenant_id: str) -> None:
        """Seeds 4 quarters of ROI benchmark data."""
        quarters = [
            ("Q4-2025", 780000.0, 10200000.0, 1207.7, 0.81, 125000.0, 2800000.0, 440000.0),
            ("Q1-2026", 810000.0, 11100000.0, 1270.4, 0.83, 132000.0, 3000000.0, 475000.0),
            ("Q2-2026", 835000.0, 11800000.0, 1312.6, 0.85, 139000.0, 3100000.0, 498000.0),
            ("Q3-2026", 850000.0, 12400000.0, 1359.0, 0.87, 145000.0, 3200000.0, 520000.0),
        ]
        for q, inv, prevented, roi, breach_red, insur, penalty, labor in quarters:
            db.add(CyberROIRecord(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                period_label=q,
                security_investment_usd=inv,
                estimated_losses_prevented_usd=prevented,
                roi_percentage=roi,
                breach_probability_reduction=breach_red,
                cyber_insurance_savings_usd=insur,
                compliance_penalty_avoidance_usd=penalty,
                automation_labor_savings_usd=labor,
                top_roi_drivers_json=[
                    "Autonomous SOAR playbooks reduced analyst hours by 68%",
                    "Zero critical breaches → full cyber insurance premium discount",
                    f"SOC2 + ISO 27001 compliance automation avoided ${penalty/1e6:.1f}M regulatory exposure"
                ],
                calculated_at=datetime.now(timezone.utc)
            ))
        await db.flush()

    @staticmethod
    def _serialize(r: CyberROIRecord) -> Dict[str, Any]:
        return {
            "id": r.id,
            "period_label": r.period_label,
            "security_investment_usd": r.security_investment_usd,
            "estimated_losses_prevented_usd": r.estimated_losses_prevented_usd,
            "roi_percentage": r.roi_percentage,
            "breach_probability_reduction": r.breach_probability_reduction,
            "cyber_insurance_savings_usd": r.cyber_insurance_savings_usd,
            "compliance_penalty_avoidance_usd": r.compliance_penalty_avoidance_usd,
            "automation_labor_savings_usd": r.automation_labor_savings_usd,
            "top_roi_drivers": r.top_roi_drivers_json,
            "calculated_at": r.calculated_at.isoformat() if r.calculated_at else None
        }
