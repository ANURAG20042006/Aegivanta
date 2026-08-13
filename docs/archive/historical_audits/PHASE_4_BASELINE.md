# PHASE 4 — BASELINE AUDIT

**Target Repository**: SentinelAI (`backend/app/`, `ml/`, `tests/`)  
**Audit Timestamp**: 2026-08-13  
**Auditor**: Antigravity Backend & API Engineering Team  

---

## Executive Summary

A comprehensive endpoint-by-endpoint data flow audit was performed tracing request validation, authentication, authorization, service logic, ML artifact loading, model inference, database queries, and response schemas.

---

## Data Flow & Integrity Findings

### 1. Artifact Loading & Unhandled Null Model Fallbacks
- **Location**: [`backend/app/services/predict_service.py:L58-L60 & L81`](file:///c:/Users/NJ542WS/Desktop/major%20project/backend/app/services/predict_service.py#L58)
- **Finding**: When `_load_artifacts(model_name)` fails to load a model artifact from disk, it caught the exception with `logger.warning` and set `cls._model_artifacts[model_name] = None`. Subsequent calls to `infer_packet_threat()` attempted attribute checks on `None`, causing unhandled exceptions instead of failing closed with HTTP 503.

### 2. Active Model Status Enforcement in DB
- **Location**: [`backend/app/services/predict_service.py:L99`](file:///c:/Users/NJ542WS/Desktop/major%20project/backend/app/services/predict_service.py#L99)
- **Finding**: `predict_service` loaded artifacts by filename directly without verifying that the corresponding `ModelRegistry` record in the database is currently marked `is_active = True`.

### 3. Static Mode Label in Remediation Dispatch Endpoint
- **Location**: [`backend/app/api/v1/predict.py:L97 & L105`](file:///c:/Users/NJ542WS/Desktop/major%20project/backend/app/api/v1/predict.py#L97)
- **Finding**: `POST /api/v1/predict/remediate` hardcoded `"mode": "SIMULATION MODE"` and `"remediation_mode": "SIMULATION MODE"` instead of dynamically resolving `settings.OPERATING_MODE` (DEMO, LAB, or PRODUCTION).

### 4. Input Vector Feature Validation Granularity
- **Location**: [`backend/app/services/predict_service.py:L103-L109`](file:///c:/Users/NJ542WS/Desktop/major%20project/backend/app/services/predict_service.py#L103)
- **Finding**: Input validation caught errors via `validate_input_vector`, but did not return structured 400 Bad Request error detail detailing feature datatype mismatch or out-of-bounds numeric constraints.

---

## Endpoint Data Flow Audit Matrix

| Method | Endpoint Path | Source of Truth | Validation | ML Inference | Audit Logged | Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `POST` | `/api/v1/predict/single` | Loaded Active Model + DB Incident | `FeatureSchema` | Real `predict()` / `predict_proba()` | Yes | REFINING FAIL-CLOSED |
| `POST` | `/api/v1/predict/csv` | Loaded Active Model + DB Incidents | CSV Column Mapping | Real `predict()` / `predict_proba()` | Yes | REFINING FAIL-CLOSED |
| `POST` | `/api/v1/predict/remediate` | `settings.OPERATING_MODE` + DB Audit | Body Schema | N/A | Yes | DYNAMIC MODE FIX |
| `GET` | `/api/v1/analytics/summary` | PostgreSQL `incidents` + `model_registry` | Query Params | N/A | No | PASS |
| `GET` | `/api/v1/analytics/roc` | `ml/artifacts/roc_curves.json` | None | N/A | No | PASS |
| `POST` | `/api/v1/train/trigger` | K-Fold CV Pipeline + DB `training_jobs` | Background Task | Multi-Model CV | Yes | PASS |
| `PATCH` | `/api/v1/incidents/{id}/status` | State Machine + DB `incidents` | State Transition | N/A | Yes | PASS |
| `POST` | `/api/v1/incidents/{id}/remediate` | `settings.OPERATING_MODE` + DB Audit | Body Schema | N/A | Yes | PASS |
