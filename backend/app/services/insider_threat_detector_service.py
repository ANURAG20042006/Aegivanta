"""
backend/app/services/insider_threat_detector_service.py
=======================================================
Phase 37 Insider Threat Defense & Flight Risk Indicator Service.
Detects mass downloads, cloud storage hoarding, and dormant credential probing.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.ai_soc_ueba import InsiderThreatIndicator

logger = logging.getLogger("Aegivanta.InsiderThreat")


class InsiderThreatDetectorService:
    """Enterprise Insider Threat & Data Hoarding Defense."""

    @classmethod
    async def list_insider_threats(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists detected insider threat indicators."""
        stmt = select(InsiderThreatIndicator).where(
            InsiderThreatIndicator.tenant_id == tenant_id
        ).order_by(desc(InsiderThreatIndicator.detected_at)).limit(limit)

        threats = list((await db.execute(stmt)).scalars().all())

        if not threats:
            # Seed default insider threat indicators
            defaults = [
                ("marcus.vance@corp.internal", "MASS_DOWNLOAD", 92, "Downloaded 450 customer contract PDFs from internal SharePoint repository within 15 minutes (28x above peer baseline)."),
                ("vikram.patel@corp.internal", "PRIVILEGE_PROBING", 78, "Attempted enumeration of 14 restricted Active Directory Domain Admin group memberships outside normal work hours."),
                ("sarah.connor@corp.internal", "CLOUD_HOARDING", 85, "Uploaded 3.2 GB of encrypted zip archives to unapproved personal Google Drive account from corp laptop.")
            ]
            for user, cat, mag, evid in defaults:
                inst = InsiderThreatIndicator(
                    tenant_id=tenant_id,
                    suspect_identity=user,
                    anomaly_category=cat,
                    anomaly_magnitude_score=mag,
                    evidence_summary=evid,
                    detected_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(InsiderThreatIndicator).where(InsiderThreatIndicator.tenant_id == tenant_id)
            threats = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": t.id,
                "suspect_identity": t.suspect_identity,
                "anomaly_category": t.anomaly_category,
                "anomaly_magnitude_score": t.anomaly_magnitude_score,
                "evidence_summary": t.evidence_summary,
                "detected_at": t.detected_at.isoformat()
            }
            for t in threats
        ]
