# AEGIVANTA — PHASE 19 REST API SPECIFICATION

## SOAR 2.0 Endpoints
- `GET /api/v1/soar/playbooks`: List declarative playbooks.
- `POST /api/v1/soar/playbooks`: Create and validate new declarative playbook.
- `POST /api/v1/soar/playbooks/{id}/execute`: Execute playbook containment workflow.
- `POST /api/v1/soar/playbooks/{id}/dry-run`: Dry-run simulate playbook workflow.
- `GET /api/v1/soar/executions`: List past SOAR execution sessions.
- `POST /api/v1/soar/decision/evaluate`: Evaluate multi-factor autonomous containment decision.
- `GET /api/v1/soar/kill-switch`: Check emergency kill switch status.
- `POST /api/v1/soar/kill-switch`: Engage or disarm emergency kill switch.
- `GET /api/v1/soar/connectors`: List registered SOAR security connectors.
- `POST /api/v1/soar/connectors/{id}/health-check`: Test connector connectivity & latency.
