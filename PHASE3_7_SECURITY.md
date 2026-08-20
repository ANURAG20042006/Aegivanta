# SentinelAI — Phase 3.7 Security & RBAC Specification

## 1. Role-Based Access Control (RBAC) Matrix

| Endpoint | Method | Role Allowed | Behavior on Violation |
| :--- | :--- | :--- | :--- |
| `/api/v1/response/evaluate` | `POST` | `admin`, `analyst`, `viewer` | `401 Unauthorized` / `403 Forbidden` |
| `/api/v1/response/actions/preview` | `POST` | `admin`, `analyst`, `viewer` | `401 Unauthorized` / `403 Forbidden` |
| `/api/v1/response/actions` | `GET` | `admin`, `analyst`, `viewer` | `401 Unauthorized` / `403 Forbidden` |
| `/api/v1/response/actions/{id}` | `GET` | `admin`, `analyst`, `viewer` | `401 Unauthorized` / `403 Forbidden` |
| `/api/v1/response/actions/{id}/audit` | `GET` | `admin`, `analyst`, `viewer` | `401 Unauthorized` / `403 Forbidden` |
| `/api/v1/response/policies` | `GET` | `admin`, `analyst`, `viewer` | `401 Unauthorized` / `403 Forbidden` |
| `/api/v1/response/statistics` | `GET` | `admin`, `analyst`, `viewer` | `401 Unauthorized` / `403 Forbidden` |
| `/api/v1/response/actions` | `POST` | `admin`, `analyst` | `403 Forbidden` for `viewer` |
| `/api/v1/response/actions/{id}/approve` | `POST` | `admin`, `analyst` | `403 Forbidden` for `viewer` |
| `/api/v1/response/actions/{id}/reject` | `POST` | `admin`, `analyst` | `403 Forbidden` for `viewer` |
| `/api/v1/response/actions/{id}/execute` | `POST` | `admin`, `analyst` | `403 Forbidden` for `viewer` |
| `/api/v1/response/actions/{id}/rollback` | `POST` | `admin`, `analyst` | `403 Forbidden` for `viewer` |
| `/api/v1/response/policies` | `POST` | `admin` | `403 Forbidden` for `analyst`, `viewer` |

---

## 2. Command Injection & Target Safety Controls

- **Zero Shell Invocation**: No usage of `os.system()`, `subprocess(shell=True)`, `eval()`, `exec()`, or unparameterized queries.
- **Target Sanitization**:
  - IP targets are validated against `ipaddress.ip_address` with restrictions on loopback (`127.0.0.0/8`) and default routes (`0.0.0.0/8`).
  - Host/Asset targets are strictly regex-validated (`^[a-zA-Z0-9_\-\.]{1,128}$`), rejecting shell metacharacters (`;`, `|`, `&`, `$`, `` ` ``).
  - User identifiers are sanitized (`^[a-zA-Z0-9_\-\.@]{1,128}$`).
- **Fail-Closed Design**: If policy evaluation fails or infrastructure adapters are unconfigured, the system defaults to `BLOCKED` (never `FAIL_OPEN`).
