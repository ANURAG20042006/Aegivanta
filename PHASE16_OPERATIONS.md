# Aegivanta — Phase 16: Operations Runbook & Triage Procedures

## 1. Incident Lifecycle Triage Runbook
1. **New Alert Ingress**: Automatic deduplication and 0–100 priority scoring.
2. **Analyst Assignment**: Reassign ownership via `POST /api/v1/incidents/{id}/assign`.
3. **Investigation & Search**: Search related entities via `POST /api/v1/investigations/search`.
4. **AI Reasoning**: Request explainability via `POST /api/v1/copilot/query`.
5. **State Transition**: Advance through `TRIAGED` -> `INVESTIGATING` -> `CONTAINED` -> `RESOLVED` -> `CLOSED`.

## 2. Emergency Kill-Switch & Rollback
- Incident state transition can be reverted to `INVESTIGATING` from `CLOSED` if new telemetry emerges.
- Gated containment actions can be rejected or rolled back via standard SOAR controls.
