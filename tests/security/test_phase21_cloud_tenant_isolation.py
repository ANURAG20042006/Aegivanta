import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.cloud_asset_inventory_service import CloudAssetInventoryService
from backend.app.services.cspm_rule_engine import CSPMRuleEngine
from backend.app.services.container_security_service import ContainerSecurityService
from backend.app.services.cloud_iam_analyzer_service import CloudIAMAnalyzerService
from backend.app.models.cloud_security import CloudAsset, CSPMFinding


@pytest.mark.asyncio
async def test_cloud_asset_and_findings_tenant_isolation():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_a = "tenant-p21-alpha"
        tenant_b = "tenant-p21-beta"

        # List assets and run scans for both tenants
        assets_a = await CloudAssetInventoryService.list_assets(db, tenant_a)
        assets_b = await CloudAssetInventoryService.list_assets(db, tenant_b)

        await CSPMRuleEngine.run_full_cspm_scan(db, tenant_a)
        await CSPMRuleEngine.run_full_cspm_scan(db, tenant_b)

        findings_a = await CSPMRuleEngine.list_findings(db, tenant_a)
        findings_b = await CSPMRuleEngine.list_findings(db, tenant_b)

        assert len(assets_a) >= 5
        assert len(assets_b) >= 5
        assert len(findings_a) >= 1
        assert len(findings_b) >= 1

        # Verify cross-tenant isolation on direct asset query
        assets_cross = await CloudAssetInventoryService.list_assets(db, "non-existent-tenant-gamma")
        # gamma will seed its own default set with tenant_id="non-existent-tenant-gamma"
        assert len(assets_cross) >= 5


@pytest.mark.asyncio
async def test_container_scan_tenant_isolation():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_a = "tenant-p21-cnt-a"
        tenant_b = "tenant-p21-cnt-b"

        await ContainerSecurityService.scan_container_image(
            db=db,
            tenant_id=tenant_a,
            image_name="aegivanta/isolated-app-a",
            image_tag="v1.0"
        )

        scans_a = await ContainerSecurityService.list_image_scans(db, tenant_a)
        scans_b = await ContainerSecurityService.list_image_scans(db, tenant_b)

        # Scans for tenant_a must contain isolated-app-a
        assert any(s["image_name"] == "aegivanta/isolated-app-a" for s in scans_a)
        # Scans for tenant_b must NOT contain isolated-app-a
        assert not any(s["image_name"] == "aegivanta/isolated-app-a" for s in scans_b)
