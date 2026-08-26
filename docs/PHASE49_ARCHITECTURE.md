# Phase 49: Autonomous Cyber Defense Control Plane & Decisive War Room

## Overview
Phase 49 establishes the apex command-and-control plane for AEGIVANTA. It orchestrates high-level autonomous cyber defense missions, coordinates live multi-agent war rooms, enforces Byzantine-resilient consensus, and guarantees bounded autonomy with instant emergency kill-switch overrides.

## Key Capabilities
1. **Autonomous Defense Missions**: Directives bounded by blast radius limits (in USD), human veto windows, and threat tiers (Low to Nation-State).
2. **Decisive Multi-Agent War Room**: Distributed AI agents (IAM, Microsegmentation, UEBA, SOAR) analyze outbreaks in parallel and reach consensus on containment plans in < 25ms.
3. **Emergency Override & Kill Switch**: Instant hardware/software pause on autonomous action dispatch while maintaining operator situational awareness.

## Data Models
- `AutonomousDefenseMission` (`autonomous_defense_missions` table)
- `DefenseWarRoomSession` (`defense_war_room_sessions` table)
- `WarRoomActionDecision` (`war_room_action_decisions` table)

## API Endpoints (`/api/v1/control-plane`)
- `GET /summary` — Control plane posture summary
- `GET /missions` — List defense missions
- `POST /missions` — Launch autonomous defense mission
- `GET /war-rooms` — List live war rooms
- `GET /war-rooms/{id}` — War room details & agent consensus
- `POST /war-rooms/{id}/kill-switch` — Toggle emergency kill switch
- `POST /war-rooms/{id}/action` — Execute tactical intervention action
