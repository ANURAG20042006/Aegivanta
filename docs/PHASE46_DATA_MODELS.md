# Phase 46 Data Models — Security Automation Studio

## AutomationPlaybook

**Table**: `automation_playbooks`

| Column | Type | Default | Description |
|---|---|---|---|
| `id` | String(36) PK | `uuid4()` | Unique playbook identifier |
| `tenant_id` | String(36) | `"default-tenant"` | Tenant isolation key |
| `name` | String(255) | — | Human-readable playbook name |
| `description` | Text | `""` | Scope and purpose description |
| `trigger_type` | String(50) | `"ON_ALERT"` | Trigger mode: `ON_ALERT`, `ON_SCHEDULE`, `ON_WEBHOOK` |
| `canvas_graph_json` | JSON | `{}` | DAG node and edge definitions |
| `status` | String(50) | `"ACTIVE"` | `ACTIVE`, `DRAFT`, `PAUSED` |
| `executions_count` | Integer | `0` | Lifetime total execution count |
| `created_at` | DateTime(TZ) | `utcnow()` | Creation timestamp |

---

## PlaybookExecutionRun

**Table**: `playbook_execution_runs`

| Column | Type | Default | Description |
|---|---|---|---|
| `id` | String(36) PK | `uuid4()` | Unique run identifier |
| `tenant_id` | String(36) | — | Tenant isolation key |
| `playbook_id` | String(36) | — | FK reference to parent playbook |
| `playbook_name` | String(255) | — | Denormalized name for audit |
| `trigger_event` | String(100) | `"ALERT_CRITICAL"` | Event that initiated the run |
| `current_step` | String(100) | `"FINAL_NOTIFICATION"` | Last step executed |
| `step_results_json` | JSON | `{}` | Per-step execution outcomes |
| `status` | String(50) | `"COMPLETED"` | `COMPLETED`, `RUNNING`, `FAILED`, `AWAITING_APPROVAL` |
| `duration_ms` | Float | `145.0` | Total wall-clock execution time |
| `started_at` | DateTime(TZ) | `utcnow()` | Run start timestamp |
| `completed_at` | DateTime(TZ) | nullable | Run completion timestamp |

---

## PlaybookTemplate

**Table**: `playbook_templates`

| Column | Type | Default | Description |
|---|---|---|---|
| `id` | String(36) PK | `uuid4()` | Template identifier |
| `tenant_id` | String(36) | — | Tenant isolation key |
| `name` | String(255) | — | Template display name |
| `category` | String(100) | `"INCIDENT_RESPONSE"` | Classification category |
| `description` | Text | `""` | Use-case description |
| `default_graph_json` | JSON | `{}` | Default DAG node/edge layout |
| `verified` | Boolean | `True` | Aegivanta certification status |

---

## Seeded Turnkey Templates

| Name | Category |
|---|---|
| AWS GuardDuty Crypto-Mining Quarantine | `CLOUD_SECURITY` |
| Dark Web Leaked Credential Reset | `IDENTITY_PROTECTION` |
| ZTNA Lateral Movement Kill Switch | `ZERO_TRUST` |
