# PHASE B2 — PRE-IMPLEMENTATION CURRENT STATE REPOSITORY AUDIT

**Audit Date**: August 26, 2026  
**Auditor**: Senior Software Architect & Production Security Engineer  
**Target Repository**: Aegivanta / SentinelAI  
**Phase**: Phase B2 — Complete Read-Only Current State Audit  

---

## 1. Executive Summary

This audit catalogs every source of non-production data, mock providers, seeded metrics, synthetic datasets, simulation paths, and fallback mechanisms discovered across the Aegivanta codebase prior to implementing Phase B2 fail-closed controls.

---

## 2. Inventory of Discovered Non-Production Data Sources

### A. Environment Configuration & Settings (`backend/app/config.py`)
1. **Default Environment Fallback**:
   - `APP_ENV = "development"`, `OPERATING_MODE = "DEMO"` as defaults if unset.
   - `DATABASE_URL = "sqlite+aiosqlite:///./sentinelai.db"` defaults to local SQLite file rather than requiring PostgreSQL in production.
2. **Ephemeral Dev Secret**:
   - `_RUNTIME_DEV_SECRET = secrets.token_urlsafe(32)` used as fallback if `SECRET_KEY` is missing in development.

---

### B. Billing Engine (`backend/app/services/billing_provider.py`)
1. **MockBillingProvider**:
   - `class MockBillingProvider(BillingProvider)` implements mock customer creation, mock checkout URLs (`cs_mock_...`), and self-signed webhook simulation.
   - `get_billing_provider()` unconditionally returns `MockBillingProvider()`.
   - **Vulnerability**: If deployed to production without a fail-closed guard, the platform silently operates on fake subscription credits.

---

### C. SOC Dashboard Aggregation Engine (`backend/app/services/soc_dashboard_service.py`)
1. **Hardcoded Fallback Timing Metrics**:
   - `avg_mttd_min = ... if mttd_list else 1.2` (Line 99)
   - `avg_mtta_min = ... if mtta_list else 3.5` (Line 100)
   - `avg_mttr_min = ... if mttr_list else 12.8` (Line 101)
   - `avg_resolve_min = ... if resolve_list else 18.4` (Line 102)
   - **Vulnerability**: When zero incidents exist in production, the dashboard displays artificial response times (`1.2 min`, `3.5 min`) instead of `NO_DATA` / `0.0`.

---

### D. Threat Intelligence Engine (`backend/app/services/threat_intel_service.py`)
1. **Static List Threat Feeds**:
   - `StaticListProvider` allows JSON-string-encoded static indicators inside `feed_url`.
   - **Risk**: Needs explicit environment tagging (`DEMO` vs `PRODUCTION`) to prevent demo IOC strings from polluting production correlation tables.

---

### E. Threat Hunting Engine (`backend/app/services/threat_hunting_service.py`)
1. **Query Fallback on Missing Database**:
   - If `db is None`, `execute_dsl_query` silently returns `[]` without raising an error.
   - **Risk**: In production, missing database connections must fail closed with an explicit error rather than silently returning empty results.

---

### F. Telemetry & Sensor Ingestion (`backend/app/services/sensor_service.py` / `telemetry_ingestion_service.py`)
1. **Missing Ingest Provenance Header**:
   - `POST /api/v1/sensors/ingest` accepts JSON/Gzip payloads but does not validate mandatory provenance headers (`X-Aegivanta-Provenance`, `is_synthetic`, `is_mock`).
   - **Vulnerability**: A production sensor endpoint could ingest synthetic benchmark flows or replay demo scripts if provenance is not validated at runtime.

---

### G. ML Inference Engine (`backend/app/services/predict_service.py`)
1. **Artifact Hash Verification Absence**:
   - `resolve_model_artifact_path()` checks file existence on disk, but does not cryptographically verify the SHA-256 digest against `results/EXP-2026-003/experiment_manifest.json` before loading `joblib` binaries.
   - **Vulnerability**: An unapproved or experimental model file could be loaded in production if the artifact directory is swapped.

---

### H. Automated Playbook & Response Dry-Runs (`backend/app/api/v1/playbooks.py` / `response.py`)
1. **Simulation Mode Endpoints**:
   - `POST /api/v1/playbooks/execute` with `is_dry_run=True` returns simulated containment responses.
   - `POST /api/v1/response/actions/preview` returns simulated blast radius projections.
   - **Observation**: These dry-run simulations are legitimate features for SOC operators, but must be explicitly labeled with provenance `source_type="SIMULATION_DRY_RUN"` so they are never stored as real containment actions.

---

## 3. Pre-B2 Architectural Risk Summary

| Subsystem | Discovered Risk | Fail-Closed Solution Required |
| :--- | :--- | :--- |
| **Settings** | Ambiguous environment variables | Single authoritative `AEGIVANTA_ENVIRONMENT` (`DEMO`, `LAB`, `PRODUCTION`) with startup fail-closed validation |
| **Billing** | Unconditional `MockBillingProvider` | Reject mock provider in `PRODUCTION`; raise `ProductionConfigurationError` |
| **Dashboard** | Hardcoded MTTD/MTTA fallback numbers | Return `None` or `0.0` with explicit `NO_DATA` status when database is empty |
| **Telemetry** | Missing provenance validation | Telemetry guard rejecting `is_synthetic=True` or `is_mock=True` in `PRODUCTION` |
| **ML Inference** | Missing SHA-256 hash checks | Verify model artifact digest against authoritative experiment manifest |
| **Database** | Default SQLite fallback | Reject SQLite database URLs in `PRODUCTION` |

---
