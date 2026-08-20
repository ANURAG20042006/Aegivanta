import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.cloud_iam_analyzer_service import CloudIAMAnalyzerService
from backend.app.services.cloud_attack_path_service import CloudAttackPathService


@pytest.mark.asyncio
async def test_cloud_iam_entitlement_risk_analysis():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p21-iam"

        analysis = await CloudIAMAnalyzerService.get_iam_risk_analysis(db, tenant_id)
        assert analysis["total_identities_audited"] >= 3
        assert analysis["stale_accounts_count"] >= 1
        assert analysis["privilege_escalation_vectors_count"] >= 1

        stale_user = next((i for i in analysis["identities"] if i["is_stale"]), None)
        assert stale_user is not None
        assert stale_user["last_activity_days"] > 90


@pytest.mark.asyncio
async def test_cloud_attack_paths():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p21-path"

        paths = await CloudAttackPathService.list_attack_paths(db, tenant_id)
        assert len(paths) >= 1

        primary_path = paths[0]
        assert "S3" in primary_path["title"] or "Exfiltration" in primary_path["title"]
        assert len(primary_path["hop_nodes"]) >= 3
        assert primary_path["blast_radius"] == "CRITICAL"
        assert len(primary_path["remediation_steps"]) >= 2
