# SentinelAI — MLOps Documentation

**Last Updated**: 2026-08-13

---

## 1. Model Lifecycle States

```
TRAINING → CANDIDATE → ACTIVE
                    ↘ ARCHIVED
                    ↘ REJECTED (promotion gate fail)
ACTIVE   → ARCHIVED (on rollback)
```

### States
| State | Description |
|:---|:---|
| `TRAINING` | `TrainingJob` queued or running |
| `CANDIDATE` | Model trained, awaiting promotion gate evaluation |
| `ACTIVE` | Current production model serving predictions |
| `ARCHIVED` | Superseded champion, retained for rollback |

---

## 2. Training Job (`/api/v1/train/trigger`)

- **Auth**: `analyst` or `admin` role required
- **Effect**: Creates a `TrainingJob` record in DB and runs `ml.train_pipeline.run_training_pipeline()` asynchronously
- **Outputs**: Serialized model artifacts (`*.joblib`), `metadata.json`, `artifact_manifest.json` in `ml/artifacts/`

---

## 3. Promotion Gate (`/api/v1/train/promote`)

- **Auth**: `admin` role only
- **Policy** (configurable, default):
  - Candidate FPR ≤ champion FPR (or champion FPR not available)
  - Candidate Recall ≥ champion Recall (or champion Recall not available)
  - Candidate latency within configured threshold
  - **Missing FPR → REJECTED** (fail closed)
  - **Missing latency → REJECTED** (fail closed)
  - **Missing Recall → REJECTED** (fail closed)
- **On PASS**: Candidate set to `ACTIVE`, champion set to `ARCHIVED`
- **On FAIL**: Candidate stays `CANDIDATE`, reason returned in response

### Per-class regression check
Each attack class FPR from CV metrics must not regress beyond configured tolerance.

---

## 4. Rollback (`/api/v1/train/rollback`)

- **Auth**: `admin` role only
- **Verification**: Candidate SHA256 hash verified against stored `preprocessor_hash` and `model_hash` in `artifact_manifest.json`
- **Hash mismatch → REJECTED**: Rollback cannot proceed with corrupt artifact
- **On SUCCESS**: Previous `ARCHIVED` model promoted to `ACTIVE`
- **On FAIL**: `ACTIVE` model unchanged

---

## 5. Artifact Integrity

All artifacts tracked in `ml/artifacts/artifact_manifest.json`:
- `preprocessor_hash`: SHA256 of `preprocessor.joblib`
- `model_hash`: SHA256 of `best_model.joblib`
- `dataset_hash`: Hash of training data fingerprint
- `feature_schema_version`: `schema-v1.0`
- `model_n_features_in`: 30 (after SelectKBest)
- `git_commit`: Git commit hash at training time

---

## 6. Latency Measurement

- Measured during training evaluation via `time.perf_counter()` over 100 inference samples
- Stored as `inference_latency_ms` in `metadata.json`
- No fabricated defaults — if latency measurement fails, stored as `None` and promotion gate rejects

---

## 7. Audit Logging

Every promotion, rollback, and training trigger writes to the `AuditLog` table:
- `user_id`, `action`, `resource_type`, `resource_id`, `detail`, `timestamp`
- Accessible via `/api/v1/logs` (admin + analyst roles)
