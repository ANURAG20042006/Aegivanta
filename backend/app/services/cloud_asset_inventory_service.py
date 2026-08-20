"""
backend/app/services/cloud_asset_inventory_service.py
=====================================================
Phase 21 Cloud & Container Asset Inventory Service.
Maintains multi-cloud asset registry across AWS, GCP, Azure, and Kubernetes.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.cloud_security import CloudAsset

logger = logging.getLogger("Aegivanta.CloudAssetInventory")

DEFAULT_CLOUD_ASSETS = [
    {
        "provider": "AWS",
        "asset_type": "STORAGE_BUCKET",
        "resource_id": "arn:aws:s3:::aegivanta-customer-financial-archive-prod",
        "resource_name": "aegivanta-customer-financial-archive-prod",
        "region": "us-east-1",
        "exposure_level": "PUBLIC_INGRESS",
        "tags": {"Environment": "Production", "DataClassification": "Confidential"},
        "configuration": {"public_read": True, "server_side_encryption": False, "versioning": True},
        "risk_score": 88.0
    },
    {
        "provider": "AWS",
        "asset_type": "VM",
        "resource_id": "i-09f4b321a567c9d01",
        "resource_name": "prod-payment-processor-node-01",
        "region": "us-east-1",
        "exposure_level": "INTERNAL",
        "tags": {"Environment": "Production", "Service": "PaymentService"},
        "configuration": {"security_groups": ["sg-0123456789abcdef0"], "open_ports": [22, 443, 8080]},
        "risk_score": 45.0
    },
    {
        "provider": "AWS",
        "asset_type": "DATABASE",
        "resource_id": "arn:aws:rds:us-east-1:123456789012:db:aegivanta-core-postgres-db",
        "resource_name": "aegivanta-core-postgres-db",
        "region": "us-east-1",
        "exposure_level": "INTERNAL",
        "tags": {"Environment": "Production", "Role": "PrimaryDB"},
        "configuration": {"engine": "postgres", "version": "15.4", "storage_encrypted": True, "publicly_accessible": False},
        "risk_score": 15.0
    },
    {
        "provider": "KUBERNETES",
        "asset_type": "K8S_POD",
        "resource_id": "k8s://prod-cluster/default/aegivanta-api-7b94c8d-k92lx",
        "resource_name": "aegivanta-api-7b94c8d-k92lx",
        "region": "us-east-1",
        "exposure_level": "PUBLIC_INGRESS",
        "tags": {"app": "aegivanta-api", "tier": "backend"},
        "configuration": {"privileged": False, "hostNetwork": False, "readOnlyRootFilesystem": True},
        "risk_score": 25.0
    },
    {
        "provider": "AWS",
        "asset_type": "IAM_ROLE",
        "resource_id": "arn:aws:iam::123456789012:role/AegivantaLambdaExecutionRole",
        "resource_name": "AegivantaLambdaExecutionRole",
        "region": "global",
        "exposure_level": "INTERNAL",
        "tags": {"ManagedBy": "Terraform"},
        "configuration": {"has_admin": True, "wildcard_actions": ["s3:*", "iam:PassRole"], "trust_policy": "lambda.amazonaws.com"},
        "risk_score": 75.0
    }
]


class CloudAssetInventoryService:
    """Discovers, registers, and inventories multi-cloud & container resources."""

    @classmethod
    async def list_assets(
        cls,
        db: AsyncSession,
        tenant_id: str,
        provider: Optional[str] = None,
        asset_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves all cloud assets filtered by provider and type."""
        stmt = select(CloudAsset).where(CloudAsset.tenant_id == tenant_id)
        if provider:
            stmt = stmt.where(CloudAsset.provider == provider.upper())
        if asset_type:
            stmt = stmt.where(CloudAsset.asset_type == asset_type.upper())

        stmt = stmt.order_by(desc(CloudAsset.risk_score))
        assets = list((await db.execute(stmt)).scalars().all())

        if not assets and not provider and not asset_type:
            # Seed default assets
            for item in DEFAULT_CLOUD_ASSETS:
                inst = CloudAsset(
                    tenant_id=tenant_id,
                    provider=item["provider"],
                    asset_type=item["asset_type"],
                    resource_id=item["resource_id"],
                    resource_name=item["resource_name"],
                    region=item["region"],
                    exposure_level=item["exposure_level"],
                    tags=item["tags"],
                    configuration=item["configuration"],
                    risk_score=item["risk_score"],
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(CloudAsset).where(CloudAsset.tenant_id == tenant_id).order_by(desc(CloudAsset.risk_score))
            assets = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": a.id,
                "provider": a.provider,
                "asset_type": a.asset_type,
                "resource_id": a.resource_id,
                "resource_name": a.resource_name,
                "region": a.region,
                "exposure_level": a.exposure_level,
                "tags": a.tags,
                "configuration": a.configuration,
                "risk_score": a.risk_score,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in assets
        ]
