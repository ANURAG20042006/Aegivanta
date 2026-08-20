import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.autonomous_response_service import AutonomousResponseService
from backend.app.core.exceptions import SentinelAIException


@pytest.mark.asyncio
async def test_get_or_create_tenant_policy():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p17-resp"
        policy = await AutonomousResponseService.get_or_create_tenant_policy(db, tenant_id)
        assert policy is not None
        assert policy.tenant_id == tenant_id
        assert policy.autonomy_level == "LEVEL_2_APPROVAL_REQUIRED"
        assert policy.is_enabled is True
        assert "ISOLATE_ENDPOINT" in (policy.allowed_actions or [])


@pytest.mark.asyncio
async def test_simulate_response_dry_run():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p17-sim"
        sim = await AutonomousResponseService.simulate_response(
            db=db,
            tenant_id=tenant_id,
            incident_id="INC-TEST-01",
            action_type="ISOLATE_ENDPOINT",
            target_entity="10.0.0.99"
        )
        assert sim["decision"] == "ALLOWED"
        assert sim["requires_approval"] is True
        assert sim["blast_radius"]["affected_assets_count"] >= 1
        assert "explanation" in sim


@pytest.mark.asyncio
async def test_execute_response_and_rollback_lifecycle():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p17-exec"
        # Execute with bypass approval for testing reversible execution
        res = await AutonomousResponseService.execute_response(
            db=db,
            tenant_id=tenant_id,
            incident_id="INC-EXEC-01",
            action_type="DISABLE_API_KEY",
            target_entity="test-key-id",
            actor="TEST_USER",
            bypass_approval=True
        )
        assert res["status"] == "EXECUTED"
        action_id = res["action_id"]

        # Rollback action
        rb = await AutonomousResponseService.rollback_response(
            db=db,
            tenant_id=tenant_id,
            action_id=action_id,
            actor="ADMIN_USER"
        )
        assert rb["status"] == "ROLLED_BACK"
        assert rb["action_id"] == action_id
