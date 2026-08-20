# Aegivanta — Phase 17: Operations Runbook & Triage Procedures

## 1. Response Approval Runbook
1. **Queue Review**: Analyst checks pending actions under `/response-approvals`.
2. **Blast Radius Inspection**: Verify affected assets, predicted business impact, and rollback availability.
3. **Execution Decision**: Approve to immediately dispatch containment or Reject to route to manual investigation.
4. **Emergency Rollback**: Trigger `POST /api/v1/autonomous-response/{id}/rollback` to revert containment if operational disruption occurs.

## 2. Continuous Validation Procedures
- Validation runs automatically on schedule; on-demand execution is triggered via `POST /api/v1/security/validation/run`.
- Any critical failure triggers high-priority alerting and automated investigation creation.
