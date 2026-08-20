# SentinelAI — Phase 3.6 Security & RBAC Specification

## 1. Authentication & Role-Based Access Control (RBAC)

SentinelAI secures all incident management, correlation, and timeline APIs via signed JWT bearer tokens and granular role boundaries.

| Role | Permissions | Endpoints Allowed |
| :--- | :--- | :--- |
| **Admin** | Full administrative privileges, user management, configuration, remediation. | All endpoints (`*`) |
| **Analyst / SOC Analyst** | Read telemetry, correlate detections, assign incidents, transition lifecycle status, submit resolution. | `/incidents/*` (Read & Write), `/predict/*`, `/threat-graph/*`, `/threat-intel/*` |
| **Viewer** | Read-only access to dashboards, statistics, timelines, and MITRE coverage. | `GET /incidents/*`, `POST /incidents/correlate` (read-only query) |

### Unauthorized & Unauthenticated Protections
- **401 Unauthorized**: Returned for missing, expired, or invalid JWT bearer tokens.
- **403 Forbidden**: Returned when viewers attempt state modification (`assign`, `status`, `resolve`, `remediate`).
- **No Secret Leakage**: Zero passwords, tokens, or private keys are exposed via API responses or application logs.

---

## 2. Kubernetes Hardening & PSS Compliance

- **Non-Root Execution**: `runAsNonRoot: true` with non-root UID (10001).
- **Capability Drops**: `drop: ["ALL"]` on all pods.
- **Privilege Escalation**: `allowPrivilegeEscalation: false`.
- **Filesystem**: Read-only root filesystem with dedicated `tmpfs` mounts for `/tmp`.
- **NetworkPolicy**: Strict ingress/egress policies isolating database, Redis, API, and worker pods.
