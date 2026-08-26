# PHASE G-0 — DATABASE & SERVICE-LEVEL TENANT ISOLATION AUDIT

**Audit Date**: August 27, 2026  
**Auditor**: Principal Security Architect & Multi-Tenant Security Auditor  
**Target Repository**: Aegivanta / SentinelAI  
**Status**: STEP 1 — BASELINE AUDIT (Read-Only)  

---

## 1. Domain Model Tenant Isolation Inventory

| Model Name | Underlying Table | `tenant_id` Column Present | Query Filter Enforcement | Isolation Rating | Finding ID |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `ProtectedAsset` | `protected_assets` | Yes (`String(36)`) | `WHERE tenant_id == ctx.tenant_id` | 🟢 Enforced | N/A |
| `Alert` | `alerts` | Yes (`String(36)`) | `WHERE tenant_id == ctx.tenant_id` | 🟢 Enforced | N/A |
| `Incident` | `incidents` | Yes (`String(36)`) | `WHERE tenant_id == ctx.tenant_id` | 🟢 Enforced | N/A |
| `Sensor` | `sensors` | Yes (`String(36)`) | `WHERE tenant_id == ctx.tenant_id` | 🟢 Enforced | N/A |
| `ThreatGraphNode` | `threat_graph_nodes` | ❌ **Missing** | Global queries without tenant check | 🔴 **Vulnerable (P0)** | `FINDING-G0-01` |
| `ThreatGraphEdge` | `threat_graph_edges` | ❌ **Missing** | Global queries without tenant check | 🔴 **Vulnerable (P0)** | `FINDING-G0-02` |
| `HuntingQuery` | `hunting_queries` | ❌ **Missing** | Global queries without tenant check | 🟡 **Vulnerable (P1)** | `FINDING-G0-03` |
| `HuntingExecution`| `hunting_executions`| ❌ **Missing** | Global queries without tenant check | 🟡 **Vulnerable (P1)** | `FINDING-G0-04` |
| `SavedHuntingQuery`| `saved_hunting_queries` | Yes (`String(36)`) | `WHERE tenant_id == ctx.tenant_id` | 🟢 Enforced | N/A |
| `ImmutableAuditRecord` | `immutable_audit_logs` | Yes (`String(36)`) | Scoped via HMAC actor & tenant | 🟢 Enforced | N/A |

---

## 2. API Endpoint Default Fallback Scan

Over 350 references across `backend/app/api/v1/` use pattern:
```python
tenant_id = context.tenant_id or "default-tenant"
```
In `PRODUCTION`, this creates an implicit fallback allowing unauthenticated or non-tenant contexts to access `"default-tenant"` resources.

**Remediation Requirement**:
Add authoritative fail-closed validation:
```python
if settings.OPERATING_MODE == "PRODUCTION" and not context.tenant_id:
    raise PermissionDeniedError("Tenant context required in PRODUCTION mode.")
```
