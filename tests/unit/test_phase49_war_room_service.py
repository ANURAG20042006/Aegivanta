"""
tests/unit/test_phase49_war_room_service.py
===========================================
Unit tests for DefenseWarRoomService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.defense_war_room_service import DefenseWarRoomService
from backend.app.models.autonomous_control_plane import (
    DefenseWarRoomSession,
    WarRoomActionDecision
)


@pytest.mark.asyncio
async def test_toggle_kill_switch():
    db = AsyncMock()
    mock_room = DefenseWarRoomSession(
        id="room-123",
        tenant_id="tenant-war-test",
        room_name="War Room Alpha",
        session_status="ACTIVE",
        threat_actor_attributed="APT29",
        severity="CRITICAL",
        kill_switch_active=False
    )
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_room
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    res = await DefenseWarRoomService.toggle_kill_switch(
        db=db,
        tenant_id="tenant-war-test",
        war_room_id="room-123",
        activate=True
    )
    assert res["kill_switch_active"] is True
    assert res["status"] == "AUTONOMOUS_EXECUTION_PAUSED"


@pytest.mark.asyncio
async def test_execute_tactical_action():
    db = AsyncMock()
    action = await DefenseWarRoomService.execute_tactical_action(
        db=db,
        tenant_id="tenant-war-test",
        war_room_id="room-123",
        action_name="Deploy Dynamic Microsegmentation Quarantine",
        action_category="ISOLATION",
        proposing_agent="Agent-NetworkFabric",
        target_entity="subnet-prod-eu-west-1a"
    )
    assert action["action_name"] == "Deploy Dynamic Microsegmentation Quarantine"
    assert action["action_category"] == "ISOLATION"
    assert action["execution_status"] == "EXECUTED"
    assert action["consensus_vote_ratio"] == 1.0


@pytest.mark.asyncio
async def test_list_war_rooms_with_mock():
    db = AsyncMock()
    mock_room = DefenseWarRoomSession(
        id="room-123",
        tenant_id="tenant-war-test",
        room_name="War Room Alpha",
        session_status="ACTIVE",
        threat_actor_attributed="APT29",
        severity="CRITICAL",
        consensus_confidence_score=0.982,
        kill_switch_active=False,
        participating_agents_json=[{"role": "IAM", "confidence": 0.99}]
    )
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_room]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    rooms = await DefenseWarRoomService.list_war_rooms(db=db, tenant_id="tenant-war-test")
    assert isinstance(rooms, list)
    assert len(rooms) >= 1
    assert rooms[0]["room_name"] == "War Room Alpha"
    assert rooms[0]["consensus_confidence_score"] == 0.982
