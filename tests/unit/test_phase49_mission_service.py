"""
tests/unit/test_phase49_mission_service.py
==========================================
Unit tests for AutonomousMissionService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.autonomous_mission_service import AutonomousMissionService
from backend.app.models.autonomous_control_plane import AutonomousDefenseMission


@pytest.mark.asyncio
async def test_create_mission():
    db = AsyncMock()
    mission = await AutonomousMissionService.create_mission(
        db=db,
        tenant_id="tenant-mission-test",
        mission_name="Operation Apex Containment",
        mission_code="MISSION-APEX-01",
        objective="Contain lateral movement outbreak.",
        threat_tier="CRITICAL",
        autonomy_level="FULL_AUTONOMY",
        blast_radius_limit_usd=75000.0
    )
    assert mission["mission_code"] == "MISSION-APEX-01"
    assert mission["mission_status"] == "ACTIVE"
    assert mission["autonomy_level"] == "FULL_AUTONOMY"
    assert mission["blast_radius_limit_usd"] == 75000.0


@pytest.mark.asyncio
async def test_list_missions_with_mock():
    db = AsyncMock()
    mock_m = AutonomousDefenseMission(
        id="m-1",
        tenant_id="tenant-mission-test",
        mission_name="Operation Aegis Overwatch",
        mission_code="MISSION-AEGIS-01",
        objective="Objective summary.",
        threat_tier="CRITICAL",
        mission_status="ACTIVE",
        autonomy_level="FULL_AUTONOMY",
        blast_radius_limit_usd=150000.0,
        actions_executed_count=84,
        threats_neutralized_count=31,
        success_rate=0.991,
        kill_switch_engaged=False
    )
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_m]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    missions = await AutonomousMissionService.list_missions(db=db, tenant_id="tenant-mission-test")
    assert isinstance(missions, list)
    assert len(missions) >= 1
    assert missions[0]["mission_code"] == "MISSION-AEGIS-01"
    assert missions[0]["success_rate"] == 0.991
