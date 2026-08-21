"""
tests/integration/test_phase49_autonomous_control_plane_flow.py
===============================================================
Integration tests for the full Autonomous Control Plane flow:
control plane posture -> mission launch -> war room orchestration -> tactical action execution -> kill switch engagement.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.control_plane_posture_service import ControlPlanePostureService
from backend.app.services.autonomous_mission_service import AutonomousMissionService
from backend.app.services.defense_war_room_service import DefenseWarRoomService


@pytest.mark.asyncio
async def test_full_autonomous_control_plane_flow():
    db = AsyncMock()
    mock_scalar = MagicMock()
    mock_scalar.scalar.return_value = 2
    db.execute.return_value = mock_scalar

    # 1. Get Control Plane Posture Summary
    summary = await ControlPlanePostureService.get_control_plane_summary(
        db=db, tenant_id="tenant-integration-cp"
    )
    assert summary["control_plane_readiness_score"] >= 95.0
    assert summary["control_plane_tier"] == "AUTONOMOUS_DECISIVE_CONTROL_PLANE"

    # 2. Launch Autonomous Defense Mission Directive
    mission = await AutonomousMissionService.create_mission(
        db=db,
        tenant_id="tenant-integration-cp",
        mission_name="Operation Hyper-Containment",
        mission_code="MISSION-HYPER-01",
        objective="Autonomous swarm zero-trust microsegmentation lockdown.",
        threat_tier="CRITICAL",
        autonomy_level="FULL_AUTONOMY",
        blast_radius_limit_usd=100000.0
    )
    assert mission["mission_code"] == "MISSION-HYPER-01"
    assert mission["mission_status"] == "ACTIVE"

    # 3. Execute Tactical Action Decision in War Room
    action = await DefenseWarRoomService.execute_tactical_action(
        db=db,
        tenant_id="tenant-integration-cp",
        war_room_id="room-auto-99",
        action_name="Isolate Compromised Kubernetes Pod",
        action_category="ISOLATION",
        proposing_agent="Agent-K8sSentinel",
        target_entity="pod-payment-gateway-7df8"
    )
    assert action["action_name"] == "Isolate Compromised Kubernetes Pod"
    assert action["execution_status"] == "EXECUTED"

    # 4. Engage Kill Switch (Emergency Human Override)
    kill_res = await DefenseWarRoomService.toggle_kill_switch(
        db=db,
        tenant_id="tenant-integration-cp",
        war_room_id="room-auto-99",
        activate=True
    )
    assert kill_res["kill_switch_active"] is True
    assert kill_res["status"] == "AUTONOMOUS_EXECUTION_PAUSED"

    # 5. Disengage Kill Switch (Resume Swarm Autonomy)
    resume_res = await DefenseWarRoomService.toggle_kill_switch(
        db=db,
        tenant_id="tenant-integration-cp",
        war_room_id="room-auto-99",
        activate=False
    )
    assert resume_res["kill_switch_active"] is False
    assert resume_res["status"] == "AUTONOMOUS_EXECUTION_RESUMED"
