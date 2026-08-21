"""
tests/unit/test_phase49_models.py
=================================
Unit tests for Phase 49 Autonomous Control Plane models.
"""

from backend.app.models.autonomous_control_plane import (
    AutonomousDefenseMission,
    DefenseWarRoomSession,
    WarRoomActionDecision
)


def test_autonomous_defense_mission_model():
    mission = AutonomousDefenseMission(
        tenant_id="tenant-mission-1",
        mission_name="Operation Aegis Overwatch",
        mission_code="MISSION-AEGIS-01",
        objective="Autonomous containment across VPCs.",
        threat_tier="CRITICAL",
        mission_status="ACTIVE",
        autonomy_level="FULL_AUTONOMY",
        blast_radius_limit_usd=150000.0,
        actions_executed_count=84,
        threats_neutralized_count=31,
        success_rate=0.991,
        kill_switch_engaged=False
    )
    assert mission.mission_code == "MISSION-AEGIS-01"
    assert mission.autonomy_level == "FULL_AUTONOMY"
    assert mission.success_rate == 0.991
    assert mission.threat_tier == "CRITICAL"


def test_defense_war_room_session_model():
    room = DefenseWarRoomSession(
        tenant_id="tenant-mission-1",
        room_name="War Room Alpha",
        session_status="ACTIVE",
        threat_actor_attributed="APT29",
        severity="CRITICAL",
        consensus_confidence_score=0.982,
        kill_switch_active=False
    )
    assert room.room_name == "War Room Alpha"
    assert room.threat_actor_attributed == "APT29"
    assert room.consensus_confidence_score == 0.982
    assert room.kill_switch_active is False


def test_war_room_action_decision_model():
    action = WarRoomActionDecision(
        tenant_id="tenant-mission-1",
        war_room_id="room-123",
        action_name="Revoke Compromised IAM Access Token",
        action_category="CONTAINMENT",
        proposing_agent="Agent-IdentitySentinel",
        consensus_vote_ratio=1.0,
        execution_status="EXECUTED",
        execution_latency_ms=24.5,
        target_entity="sa-workload@prod.internal"
    )
    assert action.action_name == "Revoke Compromised IAM Access Token"
    assert action.action_category == "CONTAINMENT"
    assert action.execution_status == "EXECUTED"
    assert action.execution_latency_ms == 24.5
