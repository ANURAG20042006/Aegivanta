# PHASE C — MULTI-TENANT ISOLATION ARCHITECTURE AUDIT

**Audit Date**: August 26, 2026  
**Auditor**: Senior Application Security Architect & Penetration Tester  
**Target Repository**: Aegivanta / SentinelAI  
**Phase**: Phase C — Read-Only Multi-Tenant Architecture & Isolation Audit  

---

## 1. Executive Summary

This architecture audit evaluates the multi-tenant isolation model, trust boundaries, authorization layers, query scoping, and communication channels of Aegivanta. The objective is to identify potential cross-tenant leakage vectors, BOLA/IDOR risks, WebSocket bleeding, and database cross-pollination.

---

## 2. Tenant Context & Identity Architecture

### A. Authoritative Server-Side Tenant Resolution (`backend/app/core/tenant.py`)
- **Mechanism**: `resolve_tenant_context(request, current_user, db)`
- **Design Principle**: Client-supplied tenant IDs (via `X-Tenant-ID` header or query param) are **never trusted blindly**.
- **Verification Rule**: The backend queries `TenantMembership` for `(user_id == current_user.id, status == 'ACTIVE')`. If a user requests access to a `tenant_id` where they lack an active membership, a `PermissionDeniedError` (HTTP 403) is immediately raised.
- **Hierarchy of Roles**: `OWNER` (100) > `ADMIN` (80) > `SECURITY_ANALYST` (60) > `RESPONDER` (50) > `API_ADMIN` (40) > `BILLING_ADMIN` (30) > `VIEWER` (10).

---

## 3. Multi-Tenant Subsystem Isolation Matrix & Risk Analysis

| Subsystem / Component | Tenant Boundary | Authorization Mechanism | Potential Cross-Tenant Path | Existing Protection | Risk |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Assets (`ProtectedAsset`)** | `tenant_id` column on asset record | `resolve_tenant_context` + query filter `WHERE tenant_id == ctx.tenant_id` | Direct ID enumeration (IDOR) via `GET /assets/{id}` | Filtered queries require matching `tenant_id` | Low |
| **Alerts (`Alert`)** | `tenant_id` column on alerts | Filtered queries + tenant context dependency | Alert ID guessing | Scoped queries strictly bound to `ctx.tenant_id` | Low |
| **Incidents (`Incident`)** | `tenant_id` column on incident | RBAC + tenant context | Cross-tenant status update / acknowledge | Status updates check `tenant_id` match | Low |
| **Sensors & Telemetry** | `tenant_id` on `Sensor` and `TelemetryBatch` | `SensorService` checks `tenant_id` | Unauthorized sensor enrollment / token rotation | Token rotation and fleet endpoints enforce `ctx.tenant_id` | Low |
| **API Keys (`ApiKey`)** | `tenant_id` FK to `tenants.id` | `require_tenant_role(ADMIN)` | Cross-tenant key revocation / viewing | Secret hashed; queries strictly filtered by `ctx.tenant_id` | Low |
| **Cloud Security (`CloudAccount`)** | `tenant_id` column | `resolve_tenant_context` | Cross-tenant AWS/Azure inventory inspection | Cloud connectors validate `tenant_id` | Low |
| **Threat Intelligence (CTI)** | Hybrid (Global feed vs Custom IOCs) | Global IOCs open; custom IOCs tenant-scoped | Custom watchlist leakage | Custom indicator queries filter by `tenant_id` | Low |
| **Threat Hunting (`HuntingQuery`)** | `tenant_id` column | DSL validator + parameterized query filter | Cross-tenant entity searches | Hunting DSL executes scoped queries | Low |
| **Billing & Invoices** | `organization_id` / `tenant_id` | `BillingProvider` + webhook HMAC verification | Fake invoice lookup | Webhooks validated against tenant organization ID | Low |
| **Audit Logs (`AuditLog`)** | `user_id` / `tenant_id` | `ImmutableAuditService` | Cross-tenant audit tampering | Tamper-evident cryptographic hash chaining | Low |
| **WebSockets Telemetry** | Active socket `tenant_id` mapping | JWT query param + user validation | Cross-tenant event broadcast | Broadcast events filtered by `tenant_id` | Low |
| **SOAR & Playbooks** | `tenant_id` on execution record | `AutonomousResponseService` | Cross-tenant containment action trigger | Playbook execution validates asset ownership | Low |

---

## 4. Key Findings & Mitigation Directives

1. **Explicit Server-Side Verification**: Ensure every endpoint accessing resources by ID explicitly includes `WHERE tenant_id == ctx.tenant_id` in its lookup clause.
2. **WebSocket Isolation**: Ensure `ConnectionManager` tags connections with `tenant_id` upon JWT authentication and filters broadcast payloads so Tenant A never receives Tenant B alerts.
3. **Cache & In-Memory Isolation**: Ensure any in-memory caches or Redis keys are namespaced as `tenant:{tenant_id}:{resource}`.

---
