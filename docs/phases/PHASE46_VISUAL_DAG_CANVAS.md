# Phase 46 Visual DAG Canvas — Security Automation Studio

## Overview

The Visual DAG Canvas provides a low-code drag-and-drop interface for building security automation workflows as Directed Acyclic Graphs (DAGs).

## Node Types

### TRIGGER Node
Entry point for all DAG executions.

**Supported trigger sources**:
- `ON_ALERT` — Real-time SIEM alert (e.g., SEVERITY == "CRITICAL")
- `ON_SCHEDULE` — Cron schedule interval (e.g., every 15 minutes)
- `ON_WEBHOOK` — External system webhook (e.g., Jira ticket creation)

### CONDITION Node
Boolean branching gate.

**Example expressions**:
- `IS_PRODUCTION == true`
- `ASSET_TYPE == "PRODUCTION_DB"`
- `ANOMALY_SCORE > 0.95`

### HUMAN_GATE Node
SOC Level 2 human approval step.

- Enforces timed timeout (default: 5 minutes)
- Dispatches PagerDuty + Slack SOC War Room notification
- Auto-denies if timeout expires
- Required before all high-impact destructive actions

### ACTION Node
Automated enforcement action.

**Examples**:
- `ISOLATE_HOST_EBPF` — eBPF kernel-level network quarantine
- `REVOKE_OKTA_SESSIONS` — Terminate all active OAuth/SAML sessions
- `DISABLE_AD_ACCOUNT` — Lock Azure AD / on-prem account

### NOTIFICATION Node
Alert dispatch to SOC and on-call channels.

**Supported integrations**:
- PagerDuty (L2 escalation)
- Slack SOC War Room
- Jira Cloud (auto-ticket)
- Email

## Sample Canvas Graph JSON

```json
{
  "nodes": [
    {"id": "node-1", "type": "TRIGGER", "title": "On Alert Critical"},
    {"id": "node-2", "type": "CONDITION", "title": "Is Production Asset?"},
    {"id": "node-3", "type": "HUMAN_GATE", "title": "SOC L2 Approval"},
    {"id": "node-4", "type": "ACTION", "title": "eBPF Host Quarantine"},
    {"id": "node-5", "type": "NOTIFICATION", "title": "PagerDuty + Slack Alert"}
  ],
  "edges": [
    {"source": "node-1", "target": "node-2"},
    {"source": "node-2", "target": "node-3", "condition": "IS_PRODUCTION == true"},
    {"source": "node-3", "target": "node-4"},
    {"source": "node-4", "target": "node-5"}
  ]
}
```
