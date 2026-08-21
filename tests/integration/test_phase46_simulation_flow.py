"""
tests/integration/test_phase46_simulation_flow.py
=================================================
Integration tests for Playbook simulation and execution verification.
"""

import pytest
from unittest.mock import AsyncMock
from backend.app.services.playbook_engine_service import PlaybookEngineService
from backend.app.services.automation_studio_posture_service import AutomationStudioPostureService


@pytest.mark.asyncio
async def test_simulation_and_posture_flow():
    db = AsyncMock()

    sim = await PlaybookEngineService.simulate_execution(
        db=db,
        tenant_id="tenant-prod",
        playbook_name="Automated Incident Triage"
    )
    assert sim["status"] == "COMPLETED"

    summary = await AutomationStudioPostureService.get_summary(db=db, tenant_id="tenant-prod")
    assert summary["overall_automation_score"] >= 95.0
    assert summary["security_tier"] == "AUTONOMOUS_DAG_SOAR_STUDIO"
    assert summary["mttr_reduction_percentage"] > 80.0
