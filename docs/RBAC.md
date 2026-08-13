# SentinelAI Role-Based Access Control (RBAC) Specification

## 1. Canonical System Roles
SentinelAI defines four canonical system roles enforced strictly on the server-side via FastAPI `require_role()` dependencies:

1. **ADMIN**
   - Full unrestricted system privileges.
   - Authorized actions: User account provisioning & management, ML model training, candidate evaluation, champion promotion, model rollback, incident state mutation, threat remediation execution, system configuration management.

2. **SOC_ANALYST (ANALYST)**
   - Incident triage, investigation, and threat containment operations.
   - Authorized actions: Packet inspection & threat prediction, incident lifecycle status updates, incident remediation execution, threat reports generation, threat analytics viewing.
   - Restricted actions: Cannot train models, promote/rollback production models, manage user accounts, or modify system configuration.

3. **RESEARCHER**
   - Empirical model analysis, feature evaluation, and research experimentation.
   - Authorized actions: Single/batch packet predictions, research artifact viewing, model evaluation analytics, threat reports generation.
   - Restricted actions: Cannot rollback production models, provision users, or execute perimeter threat containment.

4. **VIEWER**
   - Read-only dashboard monitoring.
   - Authorized actions: Single packet prediction inspection, read-only analytics, read-only incident list viewing, audit log inspection.
   - Restricted actions: Cannot execute model training/promotion/rollback, mutate incident statuses, execute remediation, or modify user accounts.

---

## 2. Server-Side API Authorization Matrix

| Method | Endpoint Path | Allowed Roles | Unauthenticated | Unauthorized |
| :--- | :--- | :--- | :---: | :---: |
| `POST` | `/api/v1/auth/login` | Public | 200 OK | N/A |
| `POST` | `/api/v1/auth/register` | Public (Viewer/Analyst only; Admin forbidden) | 201 Created | 403 Forbidden (if Admin) |
| `GET` | `/api/v1/users` | `ADMIN`, `SOC_ANALYST`, `VIEWER` | 401 | 403 |
| `POST` | `/api/v1/users` | `ADMIN` | 401 | 403 |
| `PUT` | `/api/v1/users/{id}` | `ADMIN` | 401 | 403 |
| `DELETE` | `/api/v1/users/{id}` | `ADMIN` | 401 | 403 |
| `POST` | `/api/v1/train/trigger` | `ADMIN` | 401 | 403 |
| `POST` | `/api/v1/train/models/{ver}/rollback` | `ADMIN` | 401 | 403 |
| `PATCH` | `/api/v1/incidents/{id}/status` | `ADMIN`, `SOC_ANALYST` | 401 | 403 |
| `POST` | `/api/v1/incidents/{id}/remediate` | `ADMIN`, `SOC_ANALYST` | 401 | 403 |
| `POST` | `/api/v1/predict/single` | `ADMIN`, `SOC_ANALYST`, `RESEARCHER`, `VIEWER` | 401 | 403 |
| `POST` | `/api/v1/predict/csv` | `ADMIN`, `SOC_ANALYST`, `RESEARCHER` | 401 | 403 |
| `GET` | `/api/v1/analytics/summary` | Authenticated Roles | 401 | 403 |
| `GET` | `/health` | Public | 200 OK | N/A |
| `GET` | `/ready` | Public / Gateway Probe | 200 / 503 | N/A |
