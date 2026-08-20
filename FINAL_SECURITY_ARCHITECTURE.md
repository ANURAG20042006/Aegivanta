# SentinelAI — Final Security Architecture & Hardening Guide

## Production Enterprise Security Specification

### 1. Defense-in-Depth Model

SentinelAI enforces layered security across all operational boundaries:

```
[ Edge / Ingress ] ──► TLS 1.3 Termination, CORS Whitelisting, Rate Limiting
      │
[ Authentication Layer ] ──► JWT Bearer Tokens (HS256/RS256), Expiration & Revocation
      │
[ Authorization / RBAC ] ──► Strict Role Hierarchy: Admin > Analyst > Viewer
      │
[ API & Query Security ] ──► Pydantic Input Validation, Whitelist DSL, Zero Raw SQL
      │
[ Workload Security ] ──► Non-Root UID 10001, Drop ALL Capabilities, Read-Only FS
      │
[ Network Security ] ──► Default-Deny Kubernetes NetworkPolicies, Egress Filtering
      │
[ Audit & Integrity ] ──► HMAC-SHA256 Chained Immutable Audit Trails
```

---

### 2. Role-Based Access Control (RBAC) Matrix

| Resource / Action | Viewer | Analyst | Admin |
| :--- | :---: | :---: | :---: |
| **View Dashboard, Metrics, Incidents** | ✅ Read-Only | ✅ Read-Only | ✅ Full |
| **Acknowledge & Triage Incidents** | ❌ Forbidden | ✅ Authorized | ✅ Authorized |
| **Execute Threat Hunting Queries** | ✅ Read-Only | ✅ Authorized | ✅ Authorized |
| **Manage Investigation Cases & Notes** | ❌ Forbidden | ✅ Authorized | ✅ Authorized |
| **Request SOAR Remediation** | ❌ Forbidden | ✅ Request Only | ✅ Full |
| **Approve / Execute SOAR Actions** | ❌ Forbidden | ❌ Forbidden | ✅ Authorized |
| **Trigger SOAR Rollback** | ❌ Forbidden | ❌ Forbidden | ✅ Authorized |
| **Promote / Rollback ML Models** | ❌ Forbidden | ❌ Forbidden | ✅ Authorized |
| **Submit Analyst Feedback** | ❌ Forbidden | ✅ Authorized | ✅ Authorized |
| **Trigger Database Backups** | ❌ Forbidden | ❌ Forbidden | ✅ Authorized |

---

### 3. Container & Kubernetes Hardening

- **Pod Security Standards (PSS)**: Enforced at `restricted` profile.
- **Security Context**:
  - `runAsNonRoot: true`
  - `runAsUser: 10001`
  - `allowPrivilegeEscalation: false`
  - `readOnlyRootFilesystem: true` (with `/tmp` emptyDir)
  - `capabilities: drop: ["ALL"]`
  - `seccompProfile: type: RuntimeDefault`
- **NetworkPolicies**: Explicit ingress/egress whitelisting isolating API pods, Worker pods, Redis, and PostgreSQL.
