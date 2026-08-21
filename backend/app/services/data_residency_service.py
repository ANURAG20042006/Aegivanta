"""
backend/app/services/data_residency_service.py
=============================================
Phase 42 Sovereign Data Residency Boundary & Compliance Service.
Enforces geopolitical boundaries (GDPR EU-only, FedRAMP US-only, APPI Japan).
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.multi_region_resilience import DataResidencyBoundary

logger = logging.getLogger("Aegivanta.DataResidency")


class DataResidencyService:
    """Enterprise Sovereign Data Residency Engine."""

    @classmethod
    async def list_boundaries(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists active data residency boundaries."""
        stmt = select(DataResidencyBoundary).where(
            DataResidencyBoundary.tenant_id == tenant_id
        ).order_by(desc(DataResidencyBoundary.created_at)).limit(limit)

        boundaries = list((await db.execute(stmt)).scalars().all())

        if not boundaries:
            defaults = [
                ("European Union Sovereign Vault (GDPR Art. 44)", "GDPR_EU_ONLY", "EU_WEST_1,EU_CENTRAL_1", True, True),
                ("US Federal High Impact Isolation (FedRAMP / ITAR)", "FEDRAMP_US_ONLY", "US_GOV_EAST_1,US_GOV_WEST_1", True, True),
                ("Asia-Pacific Financial Privacy Zone (APPI / MAS)", "APPI_JAPAN", "AP_NORTHEAST_1,AP_SOUTHEAST_1", True, True)
            ]
            for name, std, regs, blk, enab in defaults:
                inst = DataResidencyBoundary(
                    tenant_id=tenant_id,
                    boundary_name=name,
                    compliance_standard=std,
                    enforced_regions=regs,
                    strict_egress_block=blk,
                    enabled=enab,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(DataResidencyBoundary).where(DataResidencyBoundary.tenant_id == tenant_id)
            boundaries = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": b.id,
                "boundary_name": b.boundary_name,
                "compliance_standard": b.compliance_standard,
                "enforced_regions": b.enforced_regions,
                "strict_egress_block": b.strict_egress_block,
                "enabled": b.enabled,
                "created_at": b.created_at.isoformat()
            }
            for b in boundaries
        ]

    @classmethod
    async def create_boundary(
        cls,
        db: AsyncSession,
        tenant_id: str,
        boundary_name: str,
        compliance_standard: str = "GDPR_EU_ONLY",
        enforced_regions: str = "EU_WEST_1,EU_CENTRAL_1",
        strict_egress_block: bool = True
    ) -> Dict[str, Any]:
        """Creates a new sovereign data residency boundary."""
        boundary = DataResidencyBoundary(
            tenant_id=tenant_id,
            boundary_name=boundary_name,
            compliance_standard=compliance_standard,
            enforced_regions=enforced_regions,
            strict_egress_block=strict_egress_block,
            enabled=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(boundary)
        await db.flush()

        return {
            "id": boundary.id,
            "boundary_name": boundary.boundary_name,
            "compliance_standard": boundary.compliance_standard,
            "enforced_regions": boundary.enforced_regions,
            "strict_egress_block": boundary.strict_egress_block,
            "enabled": boundary.enabled,
            "created_at": boundary.created_at.isoformat()
        }
