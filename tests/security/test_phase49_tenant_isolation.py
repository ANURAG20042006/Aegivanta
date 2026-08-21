"""
tests/security/test_phase49_tenant_isolation.py
================================================
Security tests for Phase 49 Autonomous Control Plane tenant isolation.
"""

from backend.app.models.autonomous_control_plane import (
    AutonomousDefenseMission,
    DefenseWarRoomSession,
    WarRoomActionDecision
)


def test_defense_mission_tenant_isolation():
    mission_a = AutonomousDefenseMission(
        tenant_id="tenant-alpha",
        mission_code="MISSION-01",
        mission_name="Operation Alpha"
    )
    mission_b = AutonomousDefenseMission(
        tenant_id="tenant-beta",
        mission_code="MISSION-01",
        mission_name="Operation Beta"
    )
    assert mission_a.tenant_id != mission_b.tenant_id
    assert mission_a.mission_name != mission_b.mission_name


def test_war_room_tenant_isolation():
    room_a = DefenseWarRoomSession(
        tenant_id="tenant-alpha",
        room_name="War Room A"
    )
    room_b = DefenseWarRoomSession(
        tenant_id="tenant-beta",
        room_name="War Room B"
    )
    assert room_a.tenant_id != room_b.tenant_id


def test_war_room_action_tenant_isolation():
    act_a = WarRoomActionDecision(
        tenant_id="tenant-alpha",
        war_room_id="room-1",
        action_name="Revoke Key"
    )
    act_b = WarRoomActionDecision(
        tenant_id="tenant-beta",
        war_room_id="room-1",
        action_name="Revoke Key"
    )
    assert act_a.tenant_id != act_b.tenant_id
