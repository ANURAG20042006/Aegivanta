# SentinelAI Final Phase 2 Verified Baseline Report

> [!IMPORTANT]
> **HISTORICAL PHASE 2 BASELINE RECORD — NOT CURRENT SYSTEM STATUS**
> This document records the baseline state at the conclusion of Phase 2.
> The authoritative current system state is defined in [`docs/CURRENT_STATUS.md`](file:///c:/Users/NJ542WS/Desktop/major%20project/docs/CURRENT_STATUS.md).

**Execution Date**: 2026-08-15  
**Baseline Verification Status**: 🟢 **PHASE 2 COMPLETED**  

---

## 1. Baseline Command Execution Results

### 1.1 Git Status & Branch
```
On branch master
Your branch is up to date with 'origin/master'.
```

### 1.2 PyTest Full Test Suite (`pytest -q`)
- **Collected**: 244 items
- **Passed**: 227
- **Skipped**: 17
- **Failed**: 0
- **Duration**: 325.20s (0:05:25)
- **Status**: 🟢 **100% PASS**

### 1.3 Master Integrity & Provenance Audit (`scripts/final_integrity_audit.py`)
- **Checks Executed**: 10
- **Critical Failures**: 0
- **Warnings**: 0
- **Result**: 🟢 **ALL 10 CRITICAL CHECKS PASSED**

### 1.4 Master 10-Point Release Audit (`scripts/final_10_point_audit.py`)
- **Audit Items Executed**: 10
- **Failures**: 0
- **Result**: 🟢 **10/10 PASSED (0 Failures)**

### 1.5 Authoritative CatBoost Champion Provenance (`EXP-2026-002`)
- **Champion Model**: CatBoost (`catboost-v1.0`)
- **Model Artifact Path**: `ml/artifacts/catboost.joblib`
- **Model SHA-256**: `efb4067565f1837c3dc7ccced66c5debace56dd563b43f64c173ab68b7392e82`
- **Preprocessor Path**: `ml/artifacts/preprocessor.joblib`
- **Preprocessor SHA-256**: `e5c07b23b9a82ca28b6805e0a2eeff3c42c97b47d6816fd089dbb92d12d93691`
- **Dataset Hash**: `62aa92a7d54fe464`
- **Selected Features**: 30 Authoritative continuous features
- **CV Macro F1**: `0.9301`
- **Holdout Test Macro F1**: `0.9329`
- **Holdout Test Accuracy**: `0.9600`
- **False Positive Rate**: `0.0023`

### 1.6 Frontend Production Build (`npm run build`)
- **Status**: 🟢 **0 errors**, built with Vite in 9.04s
- **Output Bundle**: `dist/index.html` (1.04 kB), `dist/assets/index-D5gJ0On0.css` (64.50 kB), `dist/assets/index-DvWSJgie.js` (578.06 kB)

---

## 2. Invariant Baseline Verification
The system baseline has been verified against all non-negotiable criteria before freezing Phase 2.
