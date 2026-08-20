import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.advanced_hunting_service import AdvancedHuntingService


@pytest.mark.asyncio
async def test_get_hunt_templates():
    templates = await AdvancedHuntingService.get_hunt_templates()
    assert isinstance(templates, list)
    assert len(templates) >= 3
    assert any(t["technique"] == "T1110" for t in templates)


@pytest.mark.asyncio
async def test_execute_advanced_hunt():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p18-hunt"
        res = await AdvancedHuntingService.execute_hunt(
            db=db,
            tenant_id=tenant_id,
            target_entity="IP",
            query_pattern="10.0.0",
            limit=20
        )

        assert res is not None
        assert "execution_id" in res
        assert "query_duration_ms" in res
        assert res["query_duration_ms"] >= 0.0
        assert "results" in res
