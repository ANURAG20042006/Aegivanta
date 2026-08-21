# AEGIVANTA — SECURITY AUDIT REPORT

**Audit Date:** August 21, 2026  
**Auditor:** Principal Cybersecurity Engineer & DevSecOps Lead  
**Classification:** HIGH-ASSURANCE ENTERPRISE AUDIT  

---

## 1. Authentication & Session Management

### Implemented Controls
1. **Password Hashing**:
   - Implemented in `backend/app/security.py` using native `bcrypt` with random salt generation (`bcrypt.gensalt()`).
   - Maximum input truncation at 72 bytes per bcrypt specification.
   - Verification via `bcrypt.checkpw()`.
2. **JWT Credentials**:
   - Access tokens generated using `jose.jwt.encode` with `HS256` HMAC-SHA256 signature.
   - Expiration timestamps enforced via `exp` claims (`settings.ACCESS_TOKEN_EXPIRE_MINUTES`).
   - Invalidation and decoding enforced in `decode_access_token()`.
3. **MFA & Multi-Factor Auth**:
   - TOTP secret key generation and recovery codes implemented in `backend/app/services/identity_service.py`.
   - WebAuthn / Passkey support modeled in `PasskeyCredential` table.

---

## 2. Authorization & Role-Based Access Control (RBAC)

### Implemented Controls
1. **Role Normalization**:
   - `normalize_role()` maps aliases (`admin`, `administrator`, `root` → `admin`; `analyst`, `soc_analyst` → `analyst`; `viewer`, `auditor` → `viewer`).
   - Unrecognized roles normalize to `unknown`, ensuring fail-closed security.
2. **Endpoint Protection**:
   - Dependency factory `require_role(["admin", "analyst"])` attached to modifying endpoints.
   - Unauthorized role attempts return `403 Forbidden` (`PermissionDeniedError`).

---

## 3. Multi-Tenant Data Isolation

### Verification Results
1. **Context Resolution (`backend/app/core/tenant.py`)**:
   - Resolves `TenantContext` from authenticated `User` and `TenantMembership` records.
   - Client-supplied `X-Tenant-ID` is verified against active user memberships in the database; non-members receive `403 Forbidden`.
   - System administrators (`admin`, `root`) default safely to `default-tenant` when no explicit membership exists.
2. **Query-Level Partitioning**:
   - Services explicitly include `where(Model.tenant_id == tenant_id)` on all database queries.
   - Cross-tenant data leakage tests pass across all phases (`tests/security/test_phase*_tenant_isolation.py`).

---

## 4. API Security & Input Sanitization

1. **Prompt Injection Defense**:
   - Multi-pattern regex and heuristic guardrails in `AdversarialDefenseService` block jailbreaks (`DAN mode`, `system override`, `disregard rules`).
   - Secrets, JWTs, and API keys are automatically redacted (`[REDACTED_JWT]`, `[REDACTED_API_KEY]`).
2. **Rate Limiting**:
   - In-memory / Redis sliding token bucket algorithm (`backend/app/core/rate_limit.py`) throttles high-frequency extraction queries.
3. **Security Headers**:
   - `RequestTimingAndAuditMiddleware` injects:
     - `X-Content-Type-Options: nosniff`
     - `X-Frame-Options: DENY`
     - `X-XSS-Protection: 1; mode=block`
     - `Strict-Transport-Security: max-age=31536000; includeSubDomains`

---

## 5. Secret Detection Audit

- Automated pattern scan for plaintext secrets across repository.
- Default secrets in `.env.example` are strictly placeholder templates (`YourStrongAdminPassword2026!`).
- Production setting validator (`validate_production_settings()`) raises `RuntimeError` if default development secret keys are detected in production environment.
