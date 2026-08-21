"""
tests/unit/test_phase46_playbook_engine.py
==========================================
Unit tests for PlaybookEngineService execution and dry-run simulations.
"""

import pytest
from unittest.mock import AsyncMock
from backend.app.services.playbook_engine_service import PlaybookEngineService


@pytest.mark.asyncio
async def test_simulate_execution():
    db = AsyncMock()
    sim = await PlaybookEngineService.simulate_execution(
        db=db,
        tenant_id="tenant-alpha",
        playbook_name="Simulated Ransomware Containment"
    )

    assert sim["status"] == "COMPLETED"
    assert sim["step_count"] == 4
    assert sim["duration_ms"] > 0
    assert "step_1_trigger_evaluation" in sim["step_results"]
    assert "step_3_action_execution" in sim["step_results"]
