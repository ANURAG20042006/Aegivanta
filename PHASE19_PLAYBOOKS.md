# AEGIVANTA — PHASE 19 DECLARATIVE PLAYBOOKS SPECIFICATION

## 1. Playbook Schema
Declarative playbooks adhere to a structured schema:
```json
{
  "name": "C2 Intrusion Automated Rapid Containment",
  "category": "CONTAINMENT",
  "version": 1,
  "trigger_type": "ALERT_CRITICAL",
  "steps": [
    {
      "step_id": "step-1",
      "action_type": "BLOCK_IP",
      "target_entity": "198.51.100.22",
      "requires_approval": false,
      "timeout_sec": 60
    },
    {
      "step_id": "step-2",
      "action_type": "CONTAIN_ENDPOINT",
      "target_entity": "HOST-FIN-01",
      "requires_approval": true,
      "timeout_sec": 120
    }
  ]
}
```

## 2. Dry-Run Mode
When executing with `is_dry_run = True`, the engine simulates all actions, verifying connectivity, permissions, and parameters without mutating real network infrastructure.
