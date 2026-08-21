# Phase 46 Human Approval Gating — Security Automation Studio

## Overview

High-impact playbook actions that can cause irreversible changes to production systems require explicit SOC Level 2 human approval before proceeding. Phase 46 implements a structured **Human-in-the-Loop (HITL) Gate** as a first-class DAG node type.

## Trigger Criteria

A `HUMAN_GATE` node is required before any of the following action types:

| Action | Risk Level | Gate Required |
|---|---|---|
| `DISABLE_AD_ACCOUNT` | CRITICAL | ✅ Yes |
| `ISOLATE_HOST_EBPF` | CRITICAL | ✅ Yes |
| `PURGE_MAILBOX` | HIGH | ✅ Yes |
| `REVOKE_OKTA_SESSIONS` | HIGH | ✅ Yes |
| `FIREWALL_BLOCK_SUBNET` | HIGH | ✅ Yes |
| `NOTIFY_SLACK` | LOW | ❌ No |

## Approval Flow

```
1. HUMAN_GATE node reached during DAG traversal
2. PlaybookExecutionRun.status set to AWAITING_APPROVAL
3. Notification dispatched:
   - PagerDuty L2 escalation (immediate)
   - Slack SOC War Room message with approve/deny buttons
4. SOC L2 analyst reviews alert context + approves/denies
5a. APPROVED → DAG resumes from next node
5b. DENIED → Run marked FAILED, host not isolated
5c. TIMEOUT (5 min) → Auto-DENIED, safe failure mode
```

## Gate Configuration (DAG JSON)

```json
{
  "id": "gate-1",
  "type": "HUMAN_GATE",
  "title": "SOC L2 Approval",
  "config": {
    "timeout_seconds": 300,
    "on_timeout": "DENY",
    "notify_channels": ["PAGERDUTY", "SLACK_SOC_WAR_ROOM"],
    "min_approvers": 1
  }
}
```

## Audit Trail

Every gate decision is recorded in `PlaybookExecutionRun.step_results_json`:

```json
{
  "step_human_gate": {
    "status": "APPROVED",
    "approver": "sec-analyst@company.com",
    "approved_at": "2026-08-21T12:00:05Z",
    "gate_timeout_seconds": 300
  }
}
```
