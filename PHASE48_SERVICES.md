# Phase 48: AI/ML Model Platform — Service Architecture

## Services Overview

### 1. `MLModelPlatformService` (`backend/app/services/ml_model_platform_service.py`)
- **Purpose**: Manages model registry lifecycles, champion promotion, metadata tracking, and platform health scorecards.
- **Methods**:
  - `list_models(db, tenant_id, limit, offset)`: Queries registered models with defaults seeding.
  - `get_champion_model(db, tenant_id)`: Returns active production champion.
  - `register_model(db, tenant_id, model_data)`: Persists new model version and evaluates champion criteria.
  - `get_platform_summary(db, tenant_id)`: Consolidates model registry, drift, and defense metrics.

### 2. `DriftMonitoringService` (`backend/app/services/drift_monitoring_service.py`)
- **Purpose**: Computes statistical population stability index (PSI) and Kolmogorov-Smirnov distribution distance metrics against incoming telemetry streams.
- **Methods**:
  - `list_drift_records(db, tenant_id, limit)`: Returns recent feature and prediction drift evaluations.
  - `get_drift_summary(db, tenant_id)`: Computes overall drift stability rating.
  - `evaluate_feature_drift(db, tenant_id, model_id, feature_name, baseline_dist, current_dist)`: Calculates PSI and triggers retrain schedules if PSI > 0.25.

### 3. `AdversarialDefenseService` (`backend/app/services/adversarial_defense_service.py`)
- **Purpose**: Real-time mitigation against adversarial evasion, prompt injection, model extraction probing, and training data poisoning.
- **Methods**:
  - `sanitize_and_check_prompt_injection(prompt)`: Scans for regex/heuristic injection patterns and redacts secrets.
  - `protect_against_model_extraction(tenant_id, confidence, current_time)`: Injects adaptive noise and rate-limits extraction queries.
  - `validate_training_sample(features, bounds)`: Defends against poisoning anomalies.
  - `list_attack_events(db, tenant_id, limit)`: Lists blocked adversarial events.
  - `simulate_defense(db, tenant_id, model_id, attack_type, payload)`: Validates defense responses.
