# SentinelAI Phase 3 Baseline Report

**Execution Timestamp**: 2026-08-15  
**Current Branch**: `master`  
**Current Commit SHA**: `42207e9a3a33d93ed9fb61d8d8869e22766420ff`  
**Phase 1 & Phase 2 Baseline State**: 🟢 **CLEAN & VERIFIED (0 Failures, 0 Warnings)**  

---

## 1. Verified Command Execution Results

### 1.1 Git Status & Branch
```text
Branch: master
Commit: 42207e9 chore(freeze): finalize Phase 2 baseline with 227/227 passing tests, documentation demarcation, and deterministic confidence semantics
Working Tree: Clean
```

### 1.2 PyTest Suite Execution (`pytest -q`)
- **Total Collected**: 244 test items
- **Passed**: 227
- **Skipped**: 17
- **Failed**: 0
- **Duration**: 153.28s (0:02:33)
- **Status**: 🟢 **100% PASS**

### 1.3 Authoritative ML Provenance (`EXP-2026-002`)
- **Champion Model**: CatBoost (`catboost-v1.0`)
- **Artifact Path**: `ml/artifacts/catboost.joblib`
- **Artifact SHA-256**: `efb4067565f1837c3dc7ccced66c5debace56dd563b43f64c173ab68b7392e82` (Verified Match)
- **Preprocessor Path**: `ml/artifacts/preprocessor.joblib`
- **Preprocessor SHA-256**: `e5c07b23b9a82ca28b6805e0a2eeff3c42c97b47d6816fd089dbb92d12d93691` (Verified Match)
- **Feature Count**: 30 Authoritative Flow Metrics

### 1.4 Master Release Audits
- **`scripts/final_integrity_audit.py`**: 🟢 **ALL 10 CRITICAL CHECKS PASSED**
- **`scripts/final_10_point_audit.py`**: 🟢 **10/10 AUDIT ITEMS PASSED (0 FAILURES)**

### 1.5 Frontend Production Build (`npm run build`)
- **TypeScript & Vite Build**: 🟢 **0 Errors** (Compiled in 9.04s)

---

## 2. Invariant Baseline Verification
The Phase 3 development baseline is established on top of the frozen Phase 1 core and Phase 2 enrichment layer without regressions.
