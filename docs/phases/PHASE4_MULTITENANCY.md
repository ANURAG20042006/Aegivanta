# SentinelAI Phase 4 — Multi-Tenancy & Data Isolation

## 1. Multi-Tenant Entity Hierarchy

```
Organization (e.g. Acme Corp)
   ├── Subscription (PlanTier: ENTERPRISE, Quotas)
   ├── FeatureEntitlements (Explicit Flags)
   ├── TenantMemberships (Users + Roles)
   └── Tenants / Workspaces
         ├── Tenant 1 (Production Workspace)
         │      ├── Settings (Retention, MFA, Webhooks)
         │      ├── ApiKeys (sk_live_...)
         │      ├── Sensors (Enrolled Agents)
         │      ├── Incidents & Alerts
         │      ├── Threat Hunts & Investigations
         │      └── UsageRecords (Metered consumption)
         └── Tenant 2 (Staging / Lab Workspace)
```

---

## 2. Tenant Context Resolution & Security Guarantees

1. **Authentication Binding**:
   - `resolve_tenant_context` dependency extracts authenticated user from JWT token or API key.
   - User memberships are queried from `tenant_memberships` table.
   - Client-supplied `X-Tenant-ID` headers are strictly validated against active user memberships — cross-tenant impersonation is rejected with `PermissionDeniedError` (HTTP 403).

2. **Role Hierarchy**:
   - `OWNER` (100): Full organizational ownership, billing, transfer.
   - `ADMIN` (80): Workspace creation, member management, sensor management.
   - `SECURITY_ANALYST` (60): Detection, hunting, investigations, threat intel.
   - `RESPONDER` (50): SOAR response execution, containment, playbook approval.
   - `API_ADMIN` (40): API key generation, rotation, revocation.
   - `BILLING_ADMIN` (30): Plan upgrades, invoicing, checkout sessions.
   - `VIEWER` (10): Read-only dashboard access.

3. **Defense-in-Depth**:
   - Layer 1: Middleware & dependency context resolution (`TenantContext`).
   - Layer 2: API boundary role & entitlement guards (`require_tenant_role`, `require_feature`).
   - Layer 3: Database composite indexes and tenant-partitioned queries.
   - Layer 4: Append-only HMAC hash-chained immutable audit logging.
