"""
tests/unit/test_phase3_response.py
==================================
Unit tests for Controlled SOAR Approval Workflows and Safety Invariants.
"""

import pytest
from backend.app.database import AsyncSessionFactory
from backend.app.services.response_orchestrator import ResponseOrchestrator
from backend.app.models.incident import Incident


@pytest.mark.asyncio
async def test_response_approval_workflow_dryrun_enforcement():
    """Verify response action submission defaults to dry-run and requires Admin approval."""
    async with AsyncSessionFactory() as db:
        inc = Incident(
            incident_code="INC-SOAR-TEST",
            source_ip="198.51.100.12",
            destination_ip="10.0.0.1",
            source_port=44444,
            destination_port=80,
            protocol="TCP",
            packet_length=512,
            is_malicious=True,
            attack_type="DDoS",
            severity="High",
            risk_score=75.0
        )
        db.add(inc)
        await db.commit()
        await db.refresh(inc)

        # 1. Analyst requests action
        req = await ResponseOrchestrator.request_action(
            incident_id=inc.id,
            requested_action="BLOCK_IOC_SIMULATION",
            target_entity="198.51.100.12",
            requested_by="analyst",
            parameters={"rule_action": "DROP"},
            db=db
        )
        assert req.status == "REQUESTED"
        assert req.is_dry_run is True

        # 2. Non-Admin approval should fail
        with pytest.raises(PermissionError):
            await ResponseOrchestrator.approve_and_execute(
                approval_id=req.id,
                approved_by="analyst",
                approver_role="analyst",
                db=db
            )

        # 3. Admin approval succeeds in simulation dry-run mode
        result = await ResponseOrchestrator.approve_and_execute(
            approval_id=req.id,
            approved_by="admin",
            approver_role="admin",
            force_live=False,
            db=db
        )
        assert result["status"] == "COMPLETED"
        assert result["execution"]["is_dry_run"] is True
