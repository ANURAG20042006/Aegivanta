import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.soar_orchestrator_v2 import SOAROrchestratorV2
from backend.app.models.soar_v2 import DeclarativePlaybook


def test_playbook_validation_syntax():
    valid_steps = [
        {"step_id": "s1", "action_type": "BLOCK_IP", "target_entity": "198.51.100.22"},
        {"step_id": "s2", "action_type": "CONTAIN_ENDPOINT", "target_entity": "HOST-01"}
    ]
    is_valid, err = SOAROrchestratorV2.validate_playbook_definition(valid_steps)
    assert is_valid is True
    assert err is None

    invalid_steps = [
        {"step_id": "s1", "action_type": "DROP_DATABASE", "target_entity": "DB-01"}
    ]
    is_valid, err = SOAROrchestratorV2.validate_playbook_definition(invalid_steps)
    assert is_valid is False
    assert "invalid action_type" in err


@pytest.mark.asyncio
async def test_playbook_execution_and_dry_run():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p19-pb"

        pb = DeclarativePlaybook(
            tenant_id=tenant_id,
            name="Rapid Malware Isolation Test",
            category="CONTAINMENT",
            version=1,
            trigger_type="ALERT_CRITICAL",
            steps=[
                {"step_id": "s1", "action_type": "BLOCK_IP", "target_entity": "203.0.113.88"},
                {"step_id": "s2", "action_type": "REVOKE_SESSION", "target_entity": "user@corp.internal"}
            ]
        )
        db.add(pb)
        await db.flush()

        # 1. Dry Run
        dry_session = await SOAROrchestratorV2.execute_playbook_session(
            db=db,
            tenant_id=tenant_id,
            playbook_id=pb.id,
            is_dry_run=True
        )
        assert dry_session.status == "COMPLETED"
        assert dry_session.is_dry_run is True
        assert dry_session.total_steps == 2
        assert dry_session.step_results[0]["status"] == "SIMULATED_SUCCESS"

        # 2. Live Execution
        live_session = await SOAROrchestratorV2.execute_playbook_session(
            db=db,
            tenant_id=tenant_id,
            playbook_id=pb.id,
            is_dry_run=False
        )
        assert live_session.status == "COMPLETED"
        assert live_session.is_dry_run is False
        assert live_session.step_results[0]["status"] == "EXECUTED_SUCCESS"
