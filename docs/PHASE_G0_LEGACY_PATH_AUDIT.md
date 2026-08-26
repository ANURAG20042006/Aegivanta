# PHASE G-0 — LEGACY & DEAD PATH AUDIT

**Audit Date**: August 27, 2026  
**Auditor**: Principal Security Architect & SRE  
**Target Repository**: Aegivanta / SentinelAI  
**Status**: STEP 1 — BASELINE AUDIT (Read-Only)  

---

## 1. Inventory of Legacy & Duplicate Subsystems

| Path / Module | Subsystem Category | Status | Runtime Reachability | Production Reachability | Action Required | Evidence |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `backend/app/models/hunting.py` | Threat Hunting V1 | Deprecated | Low | Medium | Add `tenant_id` or route all hunting via `threat_hunting_v2.py` | `HuntingQuery` lacks tenant scoping |
| `backend/app/services/threat_hunting_service.py` | Hunting V1 Service | Deprecated | Medium | Medium | Wrap queries in explicit tenant boundaries | Replaced by `threat_hunting_v2_service.py` |
| `backend/app/models/executive_security_intelligence.py` | Executive Posture | Active | High | High | Implement fail-closed `NO_DATA` mode; disable auto-seeding in PROD | Exposes hardcoded scores if DB empty |
| `ml/models/catboost_champion.joblib` | ML (EXP-2026-002) | Historical Baseline | Retained | Retained (Lab Only) | Preserve as historical regression benchmark; ensure PROD uses EXP-2026-003 LightGBM | Manifest verified in Phase A & B0 |

---
