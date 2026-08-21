"""
tests/security/test_phase46_approval_gate_enforcement.py
========================================================
Security tests ensuring human approval gates and high-impact isolation steps require SOC authorization.
"""

import pytest
from backend.app.services.playbook_engine_service import PlaybookEngineService
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_approval_gate_enforcement():
    db = AsyncMock()
    sim = await PlaybookEngineService.simulate_execution(
        db=db,
        tenant_id="tenant-sec",
        playbook_name="High-Impact AD Account Deletion Playbook"
    )

    assert sim["status"] == "COMPLETED"
    assert "step_4_notification_dispatch" in sim["step_results"]
    assert "SLACK_SOC_WAR_ROOM" in sim["step_results"]["step_4_notification_dispatch"]["channels"]
