# SentinelAI Phase 4 — Enterprise SaaS Architecture

## 1. Logical Architecture

SentinelAI Phase 4 transforms the unified SOC platform into a multi-tenant, commercial cybersecurity SaaS platform with full workspace isolation, provider-independent billing, usage metering, and feature entitlement control.

```
Customer / Browser / Sensor Agent
    ↓
Ingress Gateway (TLS Termination + CORS + Security Headers)
    ↓
Authentication (JWT Bearer Token / Crypto-hashed API Key)
    ↓
Tenant & Security Boundary Resolution (TenantContext ContextVar)
    ↓
Feature Entitlement & Subscription Gatekeeper (FeatureEntitlementService)
    ↓
SentinelAI SOC Intelligence Platform
    ├── Multi-Model Ensemble Detection (CatBoost, LightGBM, Random Forest, XGBoost)
    ├── Threat Intelligence & Fast IOC Cache
    ├── Incident Management & MITRE ATT&CK Mapping
    ├── Threat Hunting & Investigation Workbench
    ├── Attack Graph & Lateral Movement Engine
    └── Autonomous SOAR & Safe Remediation
    ↓
Asynchronous Usage Metering (UsageMeteringService Buffer)
    ↓
Commercial Subscriptions & Billing Webhook Processing (BillingProvider)
    ↓
Multi-Tenant PostgreSQL (with Immutable HMAC Hash Chain) + Redis Streams
```

---

## 2. Key SaaS Subsystems

1. **Multi-Tenancy & Tenant Security Boundaries**:
   - `Organization`: Top-level customer entity with subscription agreement.
   - `Tenant`: Isolated workspace (production, staging, lab) with custom retention and security parameters.
   - `TenantMembership`: Role assignments (`OWNER`, `ADMIN`, `SECURITY_ANALYST`, `RESPONDER`, `VIEWER`, `BILLING_ADMIN`, `API_ADMIN`).

2. **Customer API Key Lifecycle**:
   - Keys issued with `sk_live_...` prefix.
   - Secrets displayed exactly once at creation time; stored as SHA-256 digests.
   - Scopes: `READ_TELEMETRY`, `WRITE_TELEMETRY`, `READ_INCIDENTS`, `WRITE_INCIDENTS`, `READ_THREAT_INTEL`, `RUN_HUNTS`, `EXECUTE_RESPONSE`, `READ_ANALYTICS`, `ADMIN`.

3. **Subscription & Feature Entitlements**:
   - Provider-independent abstraction (`BillingProvider`).
   - Tiers: `FREE`, `PROFESSIONAL`, `BUSINESS`, `ENTERPRISE`.
   - Feature flags enforced at API route boundaries via `require_feature(...)`.

4. **Telemetry Ingestion & Sensors**:
   - Lightweight `Sensor` agent registration with cryptographic enrollment tokens.
   - Heartbeat status monitoring and tenant attribution.

5. **Observability & Metering**:
   - Sliding-window in-memory rate limiter per tenant/user/API-key with HTTP 429 Retry-After semantics.
   - Prometheus metrics tracking SaaS request volume, active tenants, and feature usage.
