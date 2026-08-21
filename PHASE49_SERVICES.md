# Phase 49: Autonomous Control Plane — Service Architecture

## Services Overview

### 1. `AutonomousMissionService` (`backend/app/services/autonomous_mission_service.py`)
- **Purpose**: Creates, dispatches, and supervises autonomous cyber defense missions within blast-radius and veto-window constraints.
- **Methods**:
  - `list_missions(db, tenant_id, limit, offset)`: Queries active and completed defense missions.
  - `create_mission(db, tenant_id, mission_data)`: Validates financial blast radius bounds and schedules autonomous execution.
  - `get_mission(db, tenant_id, mission_id)`: Fetches mission telemetry and action history.

### 2. `DefenseWarRoomService` (`backend/app/services/defense_war_room_service.py`)
- **Purpose**: Coordinates real-time multi-agent AI war rooms, computes Byzantine consensus verdicts, and executes containment interventions.
- **Methods**:
  - `list_war_rooms(db, tenant_id, limit)`: Returns active multi-agent sessions.
  - `get_war_room(db, tenant_id, war_room_id)`: Details agent deliberation and consensus.
  - `toggle_kill_switch(db, tenant_id, war_room_id, engage, reason)`: Instantly toggles emergency kill switch.
  - `execute_tactical_action(db, tenant_id, war_room_id, action_type, target_entity, justification)`: Dispatches verified tactical actions.

### 3. `ControlPlanePostureService` (`backend/app/services/control_plane_posture_service.py`)
- **Purpose**: Aggregates autonomous posture metrics, bounded autonomy levels (Level 1 to Level 5), and consensus velocity.
- **Methods**:
  - `get_summary(db, tenant_id)`: Consolidates posture score, mission counts, and kill-switch status.
