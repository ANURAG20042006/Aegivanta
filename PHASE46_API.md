# Phase 46 API Reference — Security Automation Studio

**Base path**: `/api/v1/automation-studio`
**Tags**: `Phase 46 - Security Automation Studio`
**Auth**: Bearer token (JWT) via `resolve_tenant_context`

---

## GET /summary

Returns the SOAR Automation Studio posture scorecard.

**Response (200)**:
```json
{
  "overall_automation_score": 99.5,
  "security_tier": "AUTONOMOUS_DAG_SOAR_STUDIO",
  "active_playbooks_count": 3,
  "total_playbook_executions": 257,
  "available_turnkey_templates": 3,
  "mean_execution_duration_ms": 132.8,
  "automation_success_rate": 0.9984,
  "mttr_reduction_percentage": 88.5,
  "top_automation_priorities": ["..."],
  "evaluated_at": "2026-08-21T12:00:00Z"
}
```

---

## GET /playbooks

Lists all active DAG automation playbooks.

**Query Parameters**:
- `limit` (int, default 50, max 100)

**Response (200)**: Array of playbook objects with `canvas_graph_json` DAG structure.

---

## POST /playbooks

Creates a new DAG automation playbook.

**Request Body**:
```json
{
  "name": "Automated Lateral Movement Containment",
  "description": "Quarantines compromised host.",
  "trigger_type": "ON_ALERT"
}
```

`trigger_type` enum: `ON_ALERT`, `ON_SCHEDULE`, `ON_WEBHOOK`

---

## GET /executions

Lists playbook execution runs with step-level audit JSON.

**Response includes**: `step_results_json`, `duration_ms`, `trigger_event`, `status`.

---

## POST /simulate

Performs a dry-run simulation across all 4 DAG steps.

**Request Body**:
```json
{
  "playbook_name": "Ransomware Containment & Host Isolation",
  "trigger_payload": {"severity": "CRITICAL"}
}
```

**Response**:
```json
{
  "simulation_id": "uuid",
  "status": "COMPLETED",
  "step_count": 4,
  "duration_ms": 118.4,
  "step_results": { ... }
}
```

---

## GET /templates

Lists all verified turnkey SOAR automation templates.

**Response**: Array of templates with `category`, `description`, `default_graph_json`, `verified`.
