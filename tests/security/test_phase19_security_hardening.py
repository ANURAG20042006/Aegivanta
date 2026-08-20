import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.soar_orchestrator_v2 import SOAROrchestratorV2
from backend.app.models.soar_v2 import DeclarativePlaybook
from backend.app.models.autonomous_response import ResponseRollback
from backend.app.core.exceptions import SentinelAIException
from sqlalchemy import select


@pytest.mark.asyncio
async def test_emergency_kill_switch_blocking():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p19-ks"

        pb = DeclarativePlaybook(
            tenant_id=tenant_id,
            name="Containment Test for Kill Switch",
            category="CONTAINMENT",
            version=1,
            steps=[{"step_id": "s1", "action_type": "BLOCK_IP", "target_entity": "198.51.100.99"}]
        )
        db.add(pb)
        await db.flush()

        # Engage kill switch
        await SOAROrchestratorV2.toggle_kill_switch(db, tenant_id, active=True, reason="Simulated Emergency")

        # Attempt active execution - must be blocked with 403
        with pytest.raises(SentinelAIException) as exc_info:
            await SOAROrchestratorV2.execute_playbook_session(
                db=db,
                tenant_id=tenant_id,
                playbook_id=pb.id,
                is_dry_run=False
            )
        assert exc_info.value.status_code == 403
        assert "Kill Switch is ACTIVE" in exc_info.value.detail


@pytest.mark.asyncio
async def test_rollback_state_snapshot_generation():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p19-rb"

        pb = DeclarativePlaybook(
            tenant_id=tenant_id,
            name="Rollback Recording Playbook",
            category="CONTAINMENT",
            version=1,
            steps=[{"step_id": "s1", "action_type": "CONTAIN_ENDPOINT", "target_entity": "HOST-CORP-99"}]
        )
        db.add(pb)
        await db.flush()

        session = await SOAROrchestratorV2.execute_playbook_session(
            db=db,
            tenant_id=tenant_id,
            playbook_id=pb.id,
            is_dry_run=False
        )

        # Verify rollback record created
        rb_stmt = select(ResponseRollback).where(ResponseRollback.action_id == session.id)
        rollbacks = list((await db.execute(rb_stmt)).scalars().all())

        assert len(rollbacks) == 1
        assert rollbacks[0].action_type == "CONTAIN_ENDPOINT"
        assert rollbacks[0].rollback_status == "PENDING"

