# SentinelAI Phase 2 Security Hardening & Safety Policy

## Security Controls

1. **Role-Based Access Control (RBAC)**:
   - `admin`: Full system configuration, user management, monitoring target creation/deletion, live playbook execution.
   - `analyst`: Threat intel ingestion, incident triage, investigation triggers, simulated playbook executions.
   - `viewer`: Read-only access to dashboards, alerts, metrics, and incident history.

2. **Server-Side Request Forgery (SSRF) Prevention**:
   - Strict IP network validation prior to outbound socket connection.
   - Disallowance of internal RFC 1918 subnets, loopback addresses, link-local metadata endpoints, and non-HTTP protocols.

3. **Playbook Automation Safety**:
   - Default execution mode is strictly `is_dry_run = True` (Simulation).
   - Zero destructive network or host changes applied in simulation mode.
   - Comprehensive audit logging of all executed actions with username, target entity, parameters, and results.

4. **ML & Research Provenance Freeze**:
   - CatBoost champion artifact (`efb4067565f1837c3dc7ccced66c5debace56dd563b43f64c173ab68b7392e82`) remains strictly frozen and validated on startup.
   - Zero synthetic metric overrides or fake confidence values.
