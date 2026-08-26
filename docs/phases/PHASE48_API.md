# Phase 48: Global AI/ML Model Platform & Adversarial Defenses — API Reference

## Base URL
`/api/v1/ml-platform`

## Endpoints

### 1. Platform Posture Summary
`GET /api/v1/ml-platform/summary`
- **Description**: Returns consolidated AI/ML model platform health, active champion model, drift status, and adversarial defense score.
- **Response**: `200 OK`
```json
{
  "total_registered_models": 5,
  "champion_model_id": "cat-001",
  "champion_model_name": "CatBoost-ThreatClassifier",
  "champion_accuracy": 0.9982,
  "champion_p99_latency_ms": 3.2,
  "drift_status": "STABLE",
  "adversarial_defense_score": 99.1,
  "attacks_blocked_30d": 312
}
```

### 2. List Registered ML Models
`GET /api/v1/ml-platform/models`
- **Query Params**: `limit` (default 50), `offset` (default 0)
- **Response**: `200 OK` — List of `MLModelRegistryV2` records.

### 3. Get Active Champion Model
`GET /api/v1/ml-platform/models/champion`
- **Response**: `200 OK` — Active production champion model details.

### 4. Register New Model Version
`POST /api/v1/ml-platform/models/register`
- **Request Body**:
```json
{
  "model_name": "Transformer-NLP-PhishingDetector",
  "model_version": "v2.4.0",
  "model_family": "TRANSFORMER",
  "artifact_uri": "s3://models/nlp-v2.4.0.onnx",
  "accuracy_score": 0.9975,
  "p99_latency_ms": 3.8
}
```
- **Response**: `201 Created` — Registered model metadata.

### 5. List Statistical Drift Records
`GET /api/v1/ml-platform/drift`
- **Response**: `200 OK` — PSI and KS-statistic telemetry records.

### 6. Drift Posture Summary
`GET /api/v1/ml-platform/drift/summary`
- **Response**: `200 OK` — Aggregate drift indicators.

### 7. List Adversarial Attack Events
`GET /api/v1/ml-platform/adversarial/events`
- **Response**: `200 OK` — History of blocked evasion, extraction, and poisoning attacks.

### 8. Adversarial Defense Scorecard
`GET /api/v1/ml-platform/adversarial/summary`
- **Response**: `200 OK` — Defense metrics and attack breakdown.

### 9. Simulate Adversarial Attack Defense
`POST /api/v1/ml-platform/adversarial/simulate`
- **Request Body**:
```json
{
  "model_id": "cat-001",
  "attack_type": "EVASION",
  "attack_payload": {"sample_perturbation": 0.05}
}
```
- **Response**: `200 OK` — Simulation audit result.
