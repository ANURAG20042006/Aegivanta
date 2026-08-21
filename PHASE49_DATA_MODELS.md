# Phase 49: Autonomous Control Plane & War Room — Data Models

## Overview
Phase 49 defines database schemas for autonomous defense missions, live war rooms, and tactical decision audits.

## Models

### 1. `AutonomousDefenseMission`
Table: `autonomous_defense_missions`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `VARCHAR(64)` | Primary Key (`mission-...`) |
| `tenant_id` | `VARCHAR(64)` | Multi-tenant isolation key |
| `mission_name` | `VARCHAR(128)` | Human-readable mission name |
| `threat_tier` | `VARCHAR(32)` | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, `NATION_STATE` |
| `mission_status` | `VARCHAR(32)` | `PLANNING`, `ACTIVE`, `CONTAINED`, `COMPLETED`, `VETOED` |
| `blast_radius_limit_usd` | `FLOAT` | Max allowable financial disruption cap |
| `human_veto_window_seconds` | `INTEGER` | Time window for manual operator override |
| `scope_entities` | `JSON` | List of target hostnames, IPs, or accounts |
| `actions_taken` | `JSON` | List of autonomous actions dispatched |
| `created_at` | `DATETIME` | Timestamp created |

### 2. `DefenseWarRoomSession`
Table: `defense_war_room_sessions`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `VARCHAR(64)` | Primary Key (`war-room-...`) |
| `tenant_id` | `VARCHAR(64)` | Multi-tenant isolation key |
| `incident_title` | `VARCHAR(128)` | Outbreak / incident title |
| `severity` | `VARCHAR(32)` | `SEV1`, `SEV2`, `SEV3` |
| `status` | `VARCHAR(32)` | `ACTIVE`, `PAUSED`, `RESOLVED` |
| `kill_switch_active` | `BOOLEAN` | True if emergency kill switch engaged |
| `participating_agents` | `JSON` | List of participating AI agent specializations |
| `consensus_verdict` | `VARCHAR(64)` | Agreed tactical course of action |
| `consensus_confidence` | `FLOAT` | Byzantine consensus score (0 - 1.0) |
| `created_at` | `DATETIME` | Timestamp created |

### 3. `WarRoomActionDecision`
Table: `war_room_action_decisions`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `VARCHAR(64)` | Primary Key |
| `tenant_id` | `VARCHAR(64)` | Multi-tenant isolation key |
| `war_room_id` | `VARCHAR(64)` | Foreign key to war room |
| `action_type` | `VARCHAR(64)` | Action executed (e.g. `ISOLATE_HOST`, `REVOKE_SESSION`) |
| `target_entity` | `VARCHAR(128)` | Target entity identifier |
| `justification` | `TEXT` | Multi-agent reasoning explanation |
| `executed_by` | `VARCHAR(64)` | `AUTONOMOUS_ENGINE` or Operator Name |
| `executed_at` | `DATETIME` | Timestamp executed |
