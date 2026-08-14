# SentinelAI — Authoritative Testing Guide

**Status**: Verified & Synchronized with Repository Test Execution  
**Authoritative Source of Truth**: [`docs/CURRENT_STATUS.md`](file:///c:/Users/NJ542WS/Desktop/major%20project/docs/CURRENT_STATUS.md)  
**Last Test Execution**: **241 passed, 17 skipped, 0 failures (258 collected)**

---

## 1. Test Suite Execution Summary

| Test Category | Scope / Directory | Test Modules & Focus | Verified Pass Count |
|:---|:---|:---|:---:|
| **ML & Research Provenance** | `tests/ml/` | Zero-leakage CV, feature schema invariance, SMOTE fold isolation, metric integrity | 52 passed |
| **Security, RBAC & SSRF** | `tests/unit/test_phase2_monitoring_ssrf.py`, `tests/unit/test_phase3_security.py`, `tests/security/` | Multi-IP DNS pinning, IPv4-mapped IPv6 block, redirect validation, RBAC state transitions, SQL injection prevention | 38 passed |
| **Core Detection & API** | `tests/api/`, `tests/test_backend_api_integrity.py` | Live REST routes, JWT bearer authentication, WebSocket event streams, health probes | 42 passed |
| **XAI, Explainability & Drift** | `tests/test_drift_and_xai.py` | Real SHAP tree explanations, PSI population drift calculation, threshold triggers | 6 passed |
| **Phase 2 Intelligence & Ops** | `tests/unit/test_phase2_*.py` | Continuous monitoring checks, STIX IOC enrichment, Welford statistical anomaly detection, automated investigation evidence aggregation | 35 passed |
| **Phase 3 Advanced SOC** | `tests/unit/test_phase3_*.py` | Parameterized threat hunting, predictive risk & volume forecasting, threat intelligence graph, multi-incident campaigns, ATT&CK matrix analytics, SOAR response orchestration, SOC KPIs | 24 passed |
| **Phase 1-3 End-to-End Pipelines** | `tests/integration/` | 16-step Phase 1 pipeline (`test_complete_soc_pipeline.py`) & 25-step Phase 3 pipeline (`test_phase3_e2e.py`) | 44 passed |
| **TOTAL VERIFIED SUITE** | **Full PyTest Run** | **All non-benchmark unit, contract, security & E2E integration tests** | **241 passed, 17 skipped, 0 failures** |

---

## 2. Running the Authoritative Test Suite

### Full Test Suite Execution
```bash
python -m pytest -v
# Verified Baseline Output: 241 passed, 17 skipped in ~210s
```

### Phase-Specific Test Execution
```bash
# Phase 3 Advanced SOC & SOAR Test Suite
python -m pytest -k "phase3" -v

# Phase 2 Monitoring, Threat Intel, Anomaly & Investigation Suite
python -m pytest -k "phase2" -v

# Core ML Invariants & Data Leakage Proof Suite
python -m pytest tests/ml/ -v

# Complete Phase 3 25-Step E2E Lifecycle Pipeline
python -m pytest tests/integration/test_phase3_e2e.py -v
```

---

## 3. Critical Verified Behaviors & Assertions

| Test Function | Module | Empirical Behavior Verified |
|:---|:---|:---|
| `test_split_before_smote` | `tests/ml/test_leakage_proof.py` | Training/testing split executed prior to SMOTE; test partition never reaches oversampler |
| `test_cv_isolation` | `tests/ml/test_leakage_proof.py` | Preprocessing scalers and selectors fitted independently inside each CV fold |
| `test_fpr_formula` | `tests/test_fpr.py` | False Positive Rate calculated strictly as $\text{FP} / (\text{FP} + \text{TN})$, never as $1 - \text{recall}$ |
| `test_ssrf_protection_pinned_connection` | `tests/unit/test_phase2_monitoring_ssrf.py` | Multi-IP resolution, loopback blocking, and socket pinning prevent SSRF DNS rebinding |
| `test_hunting_query_sql_injection_defense` | `tests/unit/test_phase3_security.py` | ORM parameterized bounds neutralize SQL injection payloads (`' OR '1'='1`) with 0 unhandled exceptions |
| `test_response_approval_workflow_dryrun_enforcement` | `tests/unit/test_phase3_response.py` | Action requests default to `is_dry_run = True`; analyst role rejected on approve; admin approval completes simulation |
| `test_campaign_clustering_by_subnet` | `tests/unit/test_phase3_campaigns.py` | Common `/24` CIDR incidents clustered into campaigns with conservative `UNKNOWN` attribution |
| `test_full_phase3_operational_lifecycle_pipeline` | `tests/integration/test_phase3_e2e.py` | 25-step operational pipeline executing asset registration through CatBoost ML, IOC matching, risk scoring, threat hunting, graph generation, forecasting, ATT&CK coverage, and SOAR dry-run |

---

## 4. Intentional Skips

| Skips | Reason |
|:---|:---|
| **17 GPU / Deep-Learning Benchmark Tests** | Test host environment has no CUDA-capable GPU or tests are marked for nightly compute-intensive benchmarks (`test_deep_learning_benchmarks.py`); cleanly guarded with `@pytest.mark.skipif`. |

---

## 5. Static, Integrity & Build Verification

```bash
# 1. Python Syntax & Compilation Check
python -m compileall backend ml scripts tests
# Expected: Listing and compiling all files with 0 errors

# 2. Master 10-Point Release Audit
python scripts/final_10_point_audit.py
# Expected: ALL 10 AUDIT ITEMS PASSED (0 FAILURES)

# 3. Master Release Integrity Audit
python scripts/final_integrity_audit.py
# Expected: ALL CRITICAL CHECKS PASSED

# 4. Frontend Production Bundle Build
cd frontend && npm run build
# Expected: 0 TypeScript errors, 0 build failures, assets emitted in dist/
```
