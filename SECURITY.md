# AEGIVANTA — SECURITY POLICY & HARDENING SPECIFICATION

**Platform**: Aegivanta — Autonomous Cyber Defense & Security Operations Platform  
**Document Version**: 3.0.0  

---

## 1. Security Architecture & Threat Defense Model

Aegivanta enforces Defense-in-Depth across all computational layers:

```
[Layer 1: Edge & Network]  --> CloudFlare / Ingress TLS 1.3 / NetworkPolicy
[Layer 2: API Gateway]     --> Rate Limiting / JWT Auth / Request ID Tracking
[Layer 3: Access Control]  --> Role-Based Access Control (Admin, Analyst, Viewer)
[Layer 4: Data Security]   --> Parameterized SQL / Hash Verification / Sanitization
[Layer 5: Workload Safety] --> Non-root UID 10001 / Read-only FS / Dropped Caps
[Layer 6: SOAR Safety]     --> Fail-Closed / Zero Shell Execution / Rollback History
```

---

## 2. Authentication & Authorization Controls

### A. JWT Token Management
- **Signature Algorithm**: HMAC-SHA256 (`HS256`) with a cryptographically enforced 32+ character key (`SECRET_KEY`).
- **Token Expiration**: Configurable default of 480 minutes (8 hours) with required re-authentication.
- **Client Storage**: Managed via `aegivanta_token` in local session memory, stripped on 401 Unauthorized responses.

### B. Role-Based Access Control (RBAC) Matrix

| Endpoint Area | Viewer | Analyst | Admin |
|---|:---:|:---:|:---:|
| View Dashboard & Metrics | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| Inspect Network Telemetry | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| View Live Alerts & Incidents | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| Triage & Assign Incidents | ❌ Forbidden | ✅ Allowed | ✅ Allowed |
| Run Threat Hunting Queries | ❌ Forbidden | ✅ Allowed | ✅ Allowed |
| Trigger SOAR Containment Playbooks | ❌ Forbidden | ✅ Allowed | ✅ Allowed |
| Execute SOAR Rollback Actions | ❌ Forbidden | ❌ Forbidden | ✅ Allowed |
| Retrain / Promote ML Models | ❌ Forbidden | ❌ Forbidden | ✅ Allowed |
| Create / Delete User Accounts | ❌ Forbidden | ❌ Forbidden | ✅ Allowed |
| Configure System Settings | ❌ Forbidden | ❌ Forbidden | ✅ Allowed |

---

## 3. Vulnerability Defense Verification

| Threat Vector | Mitigation Mechanism | Verification Test |
|---|---|---|
| **SQL Injection (SQLi)** | 100% Parameterized queries via SQLAlchemy ORM; zero string concatenation. | `test_security_rbac_hardening.py` |
| **Command Injection** | Zero sub-process / `os.system` / `subprocess.Popen` execution in response actions. | Codebase Audit & SOAR Service Review |
| **Server-Side Request Forgery (SSRF)** | Private IP and loopback address blocking for webhook dispatches and external feeds. | `test_phase2_monitoring_ssrf.py` |
| **Privilege Escalation** | Public registration strictly locks accounts to `viewer` role; admin/analyst roles require admin creation. | `test_public_registration_blocks_privileged_roles` |
| **Secret Exposure** | Structured logging sanitizer redacts `password`, `token`, `secret`, `jwt`, and `api_key` before output. | `test_phase312_observability.py` |
| **Cross-Origin Resource Sharing (CORS)** | Production validator fails closed if wildcard `*` or `localhost` origins are detected. | `test_security_config.py` |
| **Container Privilege Escalation** | Kubernetes `securityContext` sets `runAsNonRoot: true`, `runAsUser: 10001`, `allowPrivilegeEscalation: false`. | `scripts/validate_k8s_manifests.py` |
