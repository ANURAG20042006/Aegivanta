# PHASE G-0 — PRODUCTION TRUTHFULNESS & HARDCODED METRICS AUDIT

**Audit Date**: August 27, 2026  
**Auditor**: Principal Security Architect, MLOps Engineer & SRE  
**Target Repository**: Aegivanta / SentinelAI  
**Status**: STEP 1 — BASELINE AUDIT (Read-Only)  

---

## 1. Executive Summary

A comprehensive scan of all services and API endpoints was conducted to identify hardcoded scores, fabricated business metrics, and default/seed fallbacks that could contaminate a `PRODUCTION` environment.

---

## 2. Inventory of Hardcoded Operational Metrics & Fallbacks

| Subsystem / Service | File Path | Suspicious Hardcoded Value(s) | Pre-Remediation Classification | Production Risk Level |
| :--- | :--- | :--- | :---: | :---: |
| **Executive Scorecard** | `backend/app/services/executive_intelligence_posture_service.py` | `score: 97.8`, `posture: 94.8`, `roi: 1359.0%`, `losses_prevented: $35.5M`, `sla: 99.91%`, `threats_blocked: 187,241` | `PRODUCTION_UNSAFE` | **P0 (Critical)** |
| **KPI Seeding Fallback** | `backend/app/services/executive_intelligence_posture_service.py` | Automatically invokes `_seed_kpi_defaults()` when DB table is empty | `PRODUCTION_UNSAFE` | **P0 (Critical)** |
| **AI Security Intel** | `backend/app/api/v1/ai_security_intelligence.py` | Implicit fallback `tenant_id = context.tenant_id or "default-tenant"` across 12 endpoints | `PRODUCTION_UNSAFE` | **P1 (High)** |
| **Attack Surface Intel** | `backend/app/api/v1/attack_surface.py` | Fallback `tenant_id = context.tenant_id or "default-tenant"` across 7 endpoints | `PRODUCTION_UNSAFE` | **P1 (High)** |
| **Cloud Security API** | `backend/app/api/v1/cloud_security.py` | Fallback `tenant_id = context.tenant_id or "default-tenant"` across 16 endpoints | `PRODUCTION_UNSAFE` | **P1 (High)** |
| **Threat Graph Nodes** | `backend/app/models/threat_graph.py` | `ThreatGraphNode` & `ThreatGraphEdge` lack `tenant_id` column | `PRODUCTION_UNSAFE` | **P0 (Critical)** |
| **Threat Hunting V1** | `backend/app/models/hunting.py` | `HuntingQuery` & `HuntingExecution` lack `tenant_id` column | `PRODUCTION_UNSAFE` | **P1 (High)** |

---

## 3. Required Remediations for Step 2+

1. **Explicit `NO_DATA` State in Production**:
   - In `PRODUCTION`, if no historical CISO reports, ROI records, or KPI snapshots exist in the database, the service must return `status: "NO_DATA"` with null/zero counts.
   - Prohibit automatic database seeding when `settings.OPERATING_MODE == "PRODUCTION"`.
2. **Strict Elimination of Implicit Default Tenant**:
   - In `PRODUCTION`, missing `context.tenant_id` must fail closed with HTTP 401/403 (`PermissionDeniedError`).
