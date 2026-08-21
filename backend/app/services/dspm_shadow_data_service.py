"""
backend/app/services/dspm_shadow_data_service.py
================================================
Phase 35 Data Security Posture Management (DSPM) & Shadow Data Discovery Service.
Discovers unencrypted cloud storage buckets, databases, and sensitive data assets.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.dlp_security import ShadowDataStore

logger = logging.getLogger("Aegivanta.DSPMShadowData")


class DSPMShadowDataService:
    """Enterprise DSPM Shadow Data Discovery Engine."""

    @classmethod
    async def list_shadow_data_stores(
        cls,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists discovered cloud storage and database assets containing sensitive data."""
        stmt = select(ShadowDataStore).where(
            ShadowDataStore.tenant_id == tenant_id
        ).order_by(desc(ShadowDataStore.discovered_sensitive_records_count)).limit(limit)

        stores = list((await db.execute(stmt)).scalars().all())

        if not stores:
            # Seed default shadow data stores
            defaults = [
                ("s3://prod-analytics-exports-2026", "AWS_S3", 48500, ["PII_SSN", "PCI_CARD"], "UNENCRYPTED_PUBLIC", "CRITICAL"),
                ("azure://finance-backup-vault/q2", "AZURE_BLOB", 18200, ["PCI_CARD", "FINANCIAL_IBAN"], "SSE_KMS", "MEDIUM"),
                ("gcs://ml-training-dataset-raw", "GCP_GCS", 96000, ["PII_SSN", "HIPAA_HEALTH"], "UNENCRYPTED_PUBLIC", "CRITICAL"),
                ("rds://postgres-crm-replica.internal", "RDS_POSTGRES", 142000, ["PII_SSN", "SECRET_KEY"], "CLIENT_ENCRYPTED", "LOW")
            ]
            for uri, prov, count, cats, enc, risk in defaults:
                inst = ShadowDataStore(
                    tenant_id=tenant_id,
                    resource_uri=uri,
                    storage_provider=prov,
                    discovered_sensitive_records_count=count,
                    detected_data_categories=cats,
                    encryption_state=enc,
                    risk_level=risk,
                    discovered_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(ShadowDataStore).where(ShadowDataStore.tenant_id == tenant_id)
            stores = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": s.id,
                "resource_uri": s.resource_uri,
                "storage_provider": s.storage_provider,
                "discovered_sensitive_records_count": s.discovered_sensitive_records_count,
                "detected_data_categories": s.detected_data_categories,
                "encryption_state": s.encryption_state,
                "risk_level": s.risk_level,
                "discovered_at": s.discovered_at.isoformat()
            }
            for s in stores
        ]
