import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.autonomous_response_service import AutonomousResponseService
from backend.app.core.exceptions import SentinelAIException


@pytest.mark.asyncio
async def test_tenant_isolated_autonomous_policies():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_a = "tenant-sec-a"
        tenant_b = "tenant-sec-b"

        pol_a = await AutonomousResponseService.get_or_create_tenant_policy(db, tenant_a)
        pol_a.autonomy_level = "LEVEL_4_FULL_AUTONOMOUS"
        await db.flush()

        pol_b = await AutonomousResponseService.get_or_create_tenant_policy(db, tenant_b)
        assert pol_b.autonomy_level == "LEVEL_2_APPROVAL_REQUIRED"
        assert pol_a.autonomy_level != pol_b.autonomy_level


@pytest.mark.asyncio
async def test_level_0_observe_denies_execution():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "tenant-observe-only"
        policy = await AutonomousResponseService.get_or_create_tenant_policy(db, tenant_id)
        policy.autonomy_level = "LEVEL_0_OBSERVE"
        await db.flush()

        with pytest.raises(SentinelAIException) as exc_info:
            await AutonomousResponseService.execute_response(
                db=db,
                tenant_id=tenant_id,
                incident_id="INC-OBS-01",
                action_type="ISOLATE_ENDPOINT",
                target_entity="10.0.0.99"
            )
        assert exc_info.value.status_code == 403
        assert "LEVEL_0_OBSERVE" in exc_info.value.detail


@pytest.mark.asyncio
async def test_blast_radius_protection_on_critical_infrastructure():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "tenant-critical-check"
        radius = await AutonomousResponseService.calculate_blast_radius(
            db=db,
            tenant_id=tenant_id,
            action_type="MASS_CONTAINMENT",
            target_entity="10.0.0.1"
        )
        assert radius.estimated_business_impact in ["HIGH", "CRITICAL"]
