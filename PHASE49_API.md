# Phase 49: Autonomous Cyber Defense Control Plane — API Reference

## Base URL
`/api/v1/control-plane`

## Endpoints

### 1. Control Plane Posture Summary
`GET /api/v1/control-plane/summary`
- **Description**: Returns apex autonomous control plane metrics including active missions, live war rooms, autonomy health score, and kill-switch status.
- **Response**: `200 OK`
```json
{
  "autonomy_posture_score": 98.6,
  "active_defense_missions": 3,
  "live_war_rooms": 2,
  "emergency_kill_switch_active": false,
  "bounded_autonomy_level": "LEVEL_4_HIGH_AUTONOMY",
  "consensus_speed_ms": 18.4,
  "veto_window_seconds": 60
}
```

### 2. List Autonomous Defense Missions
`GET /api/v1/control-plane/missions`
- **Query Params**: `limit` (default 50), `offset` (default 0)
- **Response**: `200 OK` — List of `AutonomousDefenseMission` records.

### 3. Launch Autonomous Defense Mission
`POST /api/v1/control-plane/missions`
- **Request Body**:
```json
{
  "mission_name": "Ransomware Outbreak Auto-Containment",
  "threat_tier": "CRITICAL",
  "scope_entities": ["HOST-CORP-44", "HOST-CORP-45"],
  "blast_radius_limit_usd": 50000.0,
  "human_veto_window_seconds": 30
}
```
- **Response**: `201 Created` — Initialized mission details.

### 4. List Live Defense War Rooms
`GET /api/v1/control-plane/war-rooms`
- **Response**: `200 OK` — Active multi-agent war room sessions.

### 5. Get War Room Details & Agent Consensus
`GET /api/v1/control-plane/war-rooms/{id}`
- **Response**: `200 OK` — Real-time agent deliberations, votes, and tactical containment options.

### 6. Toggle Emergency Kill Switch
`POST /api/v1/control-plane/war-rooms/{id}/kill-switch`
- **Request Body**:
```json
{
  "action": "ENGAGE_KILL_SWITCH",
  "reason": "Operator manual override during live investigation"
}
```
- **Response**: `200 OK` — Kill-switch status confirmation.

### 7. Execute Tactical Action
`POST /api/v1/control-plane/war-rooms/{id}/action`
- **Request Body**:
```json
{
  "action_type": "ISOLATE_SUBNET",
  "target_entity": "VLAN-104-FINANCE",
  "justification": "Multi-agent consensus verified active beaconing"
}
```
- **Response**: `200 OK` — Executed action decision.
