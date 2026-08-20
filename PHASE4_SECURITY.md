# SentinelAI Phase 4 — SaaS Security Architecture & Hardening

## 1. Threat Model & Countermeasures

| Threat Vector | Mitigation in SentinelAI v4.0 |
|---|---|
| **Cross-Tenant Data Leakage (IDOR)** | Server-side `TenantContext` validation; client-supplied tenant headers cross-referenced against authenticated memberships |
| **API Key Compromise** | Secrets hashed via SHA-256 (never stored plaintext); prefix indexing (`sk_live_...`); granular scopes; IP restrictions; immediate revocation |
| **Privilege Escalation** | `TENANT_ROLE_HIERARCHY` enforcement in `require_tenant_role` dependency factory; public registration restricted to `VIEWER` |
| **Webhook Forgery / Tampering** | Cryptographic HMAC-SHA256 signature verification in `BillingProvider`; replay attack defense via unique event ID tracking |
| **Resource Starvation / DoS** | Sliding-window `TenantRateLimiter` returning HTTP 429 and `Retry-After` headers; in-memory non-blocking usage buffering |
| **Credential / Secret Leakage** | `StructuredJSONFormatter` strips 15+ credential keys (passwords, JWTs, bearer tokens, API keys) from logs before writing |
| **Audit Trail Tampering** | Append-only `ImmutableAuditService` with HMAC-SHA256 hash chaining |

---

## 2. API Key Security Invariant

- Raw keys are generated using `secrets.token_hex(24)` (192 bits of cryptographic entropy).
- Displayed **only once** to the tenant administrator upon creation.
- Database records only store:
  - `key_prefix`: e.g. `sk_live_a1b2c3` (for lookup index)
  - `hashed_secret`: `sha256(raw_key)`
  - `scopes`: JSON array of authorized permissions
  - `rate_limit_rpm`: Request ceiling
