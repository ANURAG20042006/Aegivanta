# SENTINELAI — PHASE 3.8 SECURITY & RBAC SPECIFICATION

## Threat Hunting & Investigation Security Model

### 1. RBAC Permissions Matrix

| Endpoint / Operation | Viewer | Analyst | Admin |
| :--- | :---: | :---: | :---: |
| `POST /api/v1/hunting/query` | ✅ | ✅ | ✅ |
| `GET /api/v1/hunting/hunts` | ✅ | ✅ | ✅ |
| `GET /api/v1/hunting/hunts/{id}` | ✅ | ✅ | ✅ |
| `POST /api/v1/hunting/run/{id}` | ❌ (403) | ✅ | ✅ |
| `POST /api/v1/hunting/saved` | ❌ (403) | ✅ | ✅ |
| `GET /api/v1/investigations` | ✅ | ✅ | ✅ |
| `GET /api/v1/investigations/{id}` | ✅ | ✅ | ✅ |
| `POST /api/v1/investigations` | ❌ (403) | ✅ | ✅ |
| `PATCH /api/v1/investigations/{id}` | ❌ (403) | ✅ | ✅ |
| `POST /api/v1/investigations/{id}/evidence` | ❌ (403) | ✅ | ✅ |
| `POST /api/v1/investigations/{id}/notes` | ❌ (403) | ✅ | ✅ |
| `POST /api/v1/investigations/{id}/close` | ❌ (403) | ✅ | ✅ |
| `POST /api/v1/investigations/{id}/pivot` | ❌ (403) | ✅ | ✅ |
| `GET /api/v1/investigations/{id}/graph` | ✅ | ✅ | ✅ |
| `GET /api/v1/investigations/{id}/timeline` | ✅ | ✅ | ✅ |
| `GET /api/v1/investigations/{id}/risk` | ✅ | ✅ | ✅ |
| `GET /api/v1/investigations/{id}/mitre` | ✅ | ✅ | ✅ |
| `GET /api/v1/investigations/statistics` | ✅ | ✅ | ✅ |

---

### 2. SQL & Command Injection Defenses

1. **Zero Raw SQL Exposure**:
   - The query DSL translates strictly into parameterized SQLAlchemy queries with bound variables.
   - Field names and operators are validated against explicit, immutable whitelists.
2. **Zero Shell Execution**:
   - All code avoids `os.system`, `subprocess(shell=True)`, `eval`, and `exec`.
3. **Secret Protection**:
   - No JWT secrets, database connection URLs, or credentials are exposed across logs, responses, or error traces.
