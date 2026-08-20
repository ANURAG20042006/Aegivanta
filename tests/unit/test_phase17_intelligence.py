import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.security_intelligence_service import SecurityIntelligenceService


@pytest.mark.asyncio
async def test_get_coverage_gaps():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p17-intel"
        gaps = await SecurityIntelligenceService.get_coverage_gaps(db, tenant_id)

        assert isinstance(gaps, list)
        assert len(gaps) >= 1
        assert "technique_id" in gaps[0]
        assert "recommended_detection" in gaps[0]


@pytest.mark.asyncio
async def test_get_attack_paths():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p17-ap"
        paths = await SecurityIntelligenceService.get_attack_paths(db, tenant_id)

        assert isinstance(paths, list)
        assert len(paths) >= 2
        assert "recommended_cut_point" in paths[0]
        assert paths[0]["path_likelihood_pct"] > 0


@pytest.mark.asyncio
async def test_get_control_effectiveness():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p17-ctrl"
        controls = await SecurityIntelligenceService.get_control_effectiveness(db, tenant_id)

        assert isinstance(controls, list)
        assert len(controls) >= 3
        assert all(c["effectiveness_score"] >= 80.0 for c in controls)
