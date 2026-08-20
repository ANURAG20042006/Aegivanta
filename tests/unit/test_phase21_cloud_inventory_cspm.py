import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.cloud_asset_inventory_service import CloudAssetInventoryService
from backend.app.services.cspm_rule_engine import CSPMRuleEngine
from backend.app.models.cloud_security import CloudAsset


@pytest.mark.asyncio
async def test_cloud_asset_inventory_listing():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p21-inv"

        assets = await CloudAssetInventoryService.list_assets(db, tenant_id)
        assert len(assets) >= 5

        aws_assets = await CloudAssetInventoryService.list_assets(db, tenant_id, provider="AWS")
        assert len(aws_assets) >= 4
        assert all(a["provider"] == "AWS" for a in aws_assets)

        k8s_assets = await CloudAssetInventoryService.list_assets(db, tenant_id, provider="KUBERNETES")
        assert len(k8s_assets) >= 1
        assert k8s_assets[0]["asset_type"] == "K8S_POD"


@pytest.mark.asyncio
async def test_cspm_scan_and_finding_generation():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p21-cspm"

        scan_res = await CSPMRuleEngine.run_full_cspm_scan(db, tenant_id)
        assert scan_res["total_assets_scanned"] >= 5
        assert scan_res["total_open_findings"] >= 1
        assert "compliance_score" in scan_res
        assert scan_res["compliance_score"] <= 100

        findings = await CSPMRuleEngine.list_findings(db, tenant_id)
        rule_ids = [f["rule_id"] for f in findings]
        assert "CSPM-S3-001" in rule_ids
        assert "CSPM-NET-001" in rule_ids
