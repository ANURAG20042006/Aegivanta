# AEGIVANTA — PHASE 19 OPERATIONS & RUNBOOK

## 1. Playbook Execution Lifecycle
1. Trigger event matched (Critical Alert / Escalated Incident).
2. Autonomous Decision Engine checks asset criticality and confidence.
3. If Kill Switch is DISARMED and policy permits, executes step-by-step containment.
4. If approval required, enqueues request in `ResponseApproval` queue.
5. All executed steps record duration into Prometheus metric `aegivanta_soar_action_duration_seconds`.

## 2. Emergency Kill Switch Runbook
- To halt all automated response during outages: Click "ENGAGE EMERGENCY KILL SWITCH" on SOAR Command Center or issue `POST /api/v1/soar/kill-switch` with `{"is_active": true}`.
