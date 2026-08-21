"""
tests/unit/test_phase49_control_plane_posture.py
================================================
Unit tests for ControlPlanePostureService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.control_plane_posture_service import ControlPlanePostureService


@pytest.mark.asyncio
async def test_get_control_plane_summary():
    db = AsyncMock()
    mock_scalar = MagicMock()
    mock_scalar.scalar.return_value = 2
    db.execute.return_value = mock_scalar

    summary = await ControlPlanePostureService.get_control_plane_summary(
        db=db, tenant_id="tenant-cp-test"
    )
    assert summary["control_plane_readiness_score"] >= 95.0
    assert summary["control_plane_tier"] == "AUTONOMOUS_DECISIVE_CONTROL_PLANE"
    assert summary["autonomous_agents_online"] >= 10
    assert summary["agent_consensus_health"] >= 0.95
    assert summary["kill_switch_global_state"] == "DISENGAGED"
    assert summary["human_in_the_loop_override_enabled"] is True
    assert summary["total_threats_neutralized_autonomously"] >= 50
