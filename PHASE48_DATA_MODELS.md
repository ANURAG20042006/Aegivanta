# Phase 48: AI/ML Model Platform & Adversarial Defenses — Data Models

## Overview
Phase 48 introduces database models for tracking enterprise ML models, statistical feature/prediction drift records, and adversarial attack telemetry.

## Models

### 1. `MLModelRegistryV2`
Table: `ml_model_registry_v2`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `VARCHAR(64)` | Primary Key (`cat-001`, `xgb-001`, etc.) |
| `tenant_id` | `VARCHAR(64)` | Multi-tenant isolation key |
| `model_name` | `VARCHAR(128)` | Model name (e.g., `CatBoost-ThreatClassifier`) |
| `model_version` | `VARCHAR(32)` | Version string (e.g., `v3.8.1`) |
| `model_family` | `VARCHAR(32)` | `CATBOOST`, `XGBOOST`, `PYTORCH_GNN`, `TRANSFORMER`, `ISOLATION_FOREST` |
| `artifact_uri` | `VARCHAR(256)` | Storage URI |
| `accuracy_score` | `FLOAT` | Accuracy benchmark (e.g., `0.9982`) |
| `p99_latency_ms` | `FLOAT` | P99 inference latency in ms |
| `is_champion` | `BOOLEAN` | True if active production champion |
| `deployment_status` | `VARCHAR(32)` | `PRODUCTION`, `CANARY`, `STAGING`, `ARCHIVED` |
| `created_at` | `DATETIME` | Timestamp registered |

### 2. `MLModelDriftRecord`
Table: `ml_model_drift_records`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `VARCHAR(64)` | Primary Key |
| `tenant_id` | `VARCHAR(64)` | Multi-tenant isolation key |
| `model_id` | `VARCHAR(64)` | Foreign key to model |
| `model_name` | `VARCHAR(128)` | Denormalized model name |
| `drift_type` | `VARCHAR(32)` | `FEATURE_DRIFT`, `PREDICTION_DRIFT`, `CONCEPT_DRIFT` |
| `feature_name` | `VARCHAR(64)` | Feature evaluated |
| `psi_score` | `FLOAT` | Population Stability Index (PSI) |
| `ks_statistic` | `FLOAT` | Kolmogorov-Smirnov test statistic |
| `drift_detected` | `BOOLEAN` | True if threshold exceeded |
| `action_taken` | `VARCHAR(64)` | Mitigation (e.g., `TRIGGER_RETRAIN_SCHEDULE`) |
| `evaluated_at` | `DATETIME` | Timestamp evaluated |

### 3. `AdversarialAttackEvent`
Table: `adversarial_attack_events`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `VARCHAR(64)` | Primary Key |
| `tenant_id` | `VARCHAR(64)` | Multi-tenant isolation key |
| `model_id` | `VARCHAR(64)` | Target model ID |
| `model_name` | `VARCHAR(128)` | Target model name |
| `attack_type` | `VARCHAR(32)` | `EVASION`, `MODEL_EXTRACTION`, `MEMBERSHIP_INFERENCE`, `POISONING` |
| `attack_severity` | `VARCHAR(32)` | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `attack_vector_json` | `JSON` | Payload / metadata of attack |
| `confidence_score` | `FLOAT` | Defense detection confidence |
| `defense_mechanism` | `VARCHAR(128)` | Applied defense technique |
| `blocked` | `BOOLEAN` | True if blocked |
| `defense_latency_ms` | `FLOAT` | Defense execution latency in ms |
| `detected_at` | `DATETIME` | Timestamp detected |
