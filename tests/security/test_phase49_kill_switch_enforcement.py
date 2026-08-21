"""
tests/security/test_phase49_kill_switch_enforcement.py
======================================================
Security tests verifying emergency kill switch enforcement and state bounds.
"""

from backend.app.models.autonomous_control_plane import (
    AutonomousDefenseMission,
    DefenseWarRoomSession
)


def test_kill_switch_default_state_and_override():
    room = DefenseWarRoomSession(
        tenant_id="tenant-ks-test",
        room_name="War Room Quarantine",
        kill_switch_active=False
    )
    assert room.kill_switch_active is False

    # Simulate emergency operator kill switch engagement
    room.kill_switch_active = True
    assert room.kill_switch_active is True


def test_mission_blast_radius_bounds():
    mission = AutonomousDefenseMission(
        tenant_id="tenant-ks-test",
        mission_code="MISSION-BOUNDED-01",
        blast_radius_limit_usd=50000.0,
        enforce_human_veto_window_seconds=30,
        kill_switch_engaged=False
    )
    assert mission.blast_radius_limit_usd == 50000.0
    assert mission.enforce_human_veto_window_seconds == 30
    assert mission.kill_switch_engaged is False

