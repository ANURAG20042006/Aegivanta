# SentinelAI — Phase 2 Baseline Report

**Baseline Branch**: `phase-2`  
**Base Commit SHA**: `19978ba5e6b752153fcd6df5e0d788c5bc5ebfc6`  
**Creation Date**: 2026-08-15  
**Operating Mode**: `DEMO` / `LAB` / `PRODUCTION`  

---

## 1. Phase 1 Verification Summary

The Phase 1 baseline test count is determined by executing the frozen `phase-2` baseline checkout. That collected count becomes the authoritative regression baseline; no hardcoded test count is assumed a priori.

| Component | Status | Metrics / Details |
|:---|:---|:---|
| **PyTest Baseline Suite** | 🟢 **PASSED** | **193 passed, 17 skipped, 0 failures** (210 collected baseline) |
| **Frontend Build** | 🟢 **PASSED** | `tsc && vite build` completed with 0 errors in 3.38s |
| **Docker Compose** | 🟢 **PASSED** | Validated YAML with `postgres`, `redis`, `backend`, `frontend` services |
| **Artifact Integrity** | 🟢 **PASSED** | `scripts/final_integrity_audit.py` passed with 0 failures, 0 warnings |
| **Master 10-Point Audit** | 🟢 **PASSED** | `scripts/final_10_point_audit.py` passed 10/10 checks |

---

## 2. Frozen ML & Experiment Provenance (`EXP-2026-002`)

| Attribute | Authoritative Frozen Value |
|:---|:---|
| **Champion Model** | `CatBoost` (`catboost-v1.0`) |
| **Model Artifact** | `ml/artifacts/catboost.joblib` / `ml/artifacts/best_model.joblib` |
| **Model SHA-256** | `efb4067565f1837c3dc7ccced66c5debace56dd563b43f64c173ab68b7392e82` |
| **Preprocessor Artifact** | `ml/artifacts/preprocessor.joblib` |
| **Preprocessor SHA-256**| `e5c07b23b9a82ca23d8c83a74659b82e2124508ec399222cfd86c8f4fc5f2849` |
| **Feature Schema** | `schema-v1.0` (30 selected continuous flow features) |
| **CV Macro F1 Score** | `0.9301 ± 0.0245` (3-Fold Stratified CV on training split) |
| **CV Accuracy** | `0.9625 ± 0.0148` |
| **Holdout Test F1** | `0.9329` (Evaluated ONCE on untouched 100-sample test set) |
| **Holdout Test Accuracy**| `0.9600` |
| **Holdout Test FPR** | `0.0023` |
| **Inference Latency** | `0.0184 ms/sample` |

---

## 3. Existing Phase 1 Architecture Summary

The existing Phase 1 architecture executes the following unified SOC detection and correlation pipeline:

```
Network Flow Telemetry / PCAP
          ↓
Feature Validation (schema-v1.0, 30 features)
          ↓
ML Preprocessing & CatBoost Inference
          ↓
Protected Asset Matching (IP, CIDR, Hostname)
          ↓
Dynamic Risk Engine (0–100 Multi-Factor Score)
          ↓
Alert Creation & Persistence
          ↓
Deterministic Incident Correlation (300s window, asset/threat grouping)
          ↓
Chronological Incident Timeline & Mitigations
          ↓
WebSocket Broadcast (/ws/threats)
          ↓
React SOC Dashboard UI
```

---

## 4. Phase 2 Architectural Objectives & Boundaries

Phase 2 will be developed as a **modular, additive layer** on top of this verified baseline without altering or duplicating the Phase 1 pipeline:

1. **Continuous Asset Monitoring**: Configurable website, API, server, and endpoint health polling with SSRF protection, strict URL validation, and timeout controls.
2. **Health Intelligence**: Uptime tracking, latency metrics, TLS expiration, DNS diagnostics, and debounce thresholding.
3. **Threat Intelligence & Ingestion**: Normalized IOC database (IPv4, IPv6, Domain, URL, Hash), pluggable feed provider framework, and attribution tracking.
4. **IOC Enrichment**: Attaches threat intelligence metadata to incoming security events without modifying raw ML predictions.
5. **Behavioral Baselines & Explainable Anomaly Detection**: Asset-specific rolling traffic volume, error rates, and connection diversity baselines.
6. **Multi-Signal Policy**: Extends existing risk scoring with transparent, documented evidence weights.
7. **Attack-Chain Analysis**: MITRE ATT&CK stage mapping (Reconnaissance to Impact) based on empirical event evidence.
8. **Automated Investigations & Recommendations**: Deterministic evidence aggregation and actionable, RBAC-safe analyst recommendations.
9. **Automation / Playbooks**: Safe execution framework defaulting to **DRY RUN / SIMULATION** mode.
10. **Advanced SOC Views**: Dedicated dashboard views for `/monitoring`, `/threat-intelligence`, `/analytics`, `/investigations`, and `/attack-chains`.
