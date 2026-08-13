# 🔬 SentinelAI Phase 7 — Real Async Retraining Audit Report

**Audit Date**: August 12, 2026  
**Job Table**: `TrainingJob`  
**Job States**: `QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`, `REJECTED`, `PROMOTED`  

---

## 1. Executive Summary & Verification

Phase 7 implements **Persisted Real Asynchronous Retraining**:
1. Invoking `POST /api/v1/train/trigger` creates an actual database `TrainingJob` record in state `QUEUED` and commits it to the database **before** returning `{"job_id": job.id, "status": "QUEUED", "created_at": ...}`.
2. The background worker task (`async_train_worker`) updates the job status to `RUNNING`, executes the leakage-free training pipeline, evaluates the candidate against the Multi-Metric Promotion Gate, and records performance metrics.
3. If training encounters errors, the job state transitions to `FAILED`, the error message is recorded, and the active production model is preserved untouched.
4. If candidate evaluation fails the promotion gate, the job state transitions to `REJECTED`, the rejection reason is stored, and the active production model remains untouched.
5. If candidate passes promotion, the job state transitions to `PROMOTED`, the new model is set to `ACTIVE` in `ModelRegistry`, the previous active model is marked `ARCHIVED`, and the `PredictService` artifact cache is invalidated.

---

## 2. Training Job Lifecycle State Machine

```
              [ POST /api/v1/train/trigger ]
                             │
                             ▼
                        ( QUEUED )
                             │
                             ▼
                        ( RUNNING )
                             │
             ┌───────────────┼───────────────┐
             │               │               │
      [ Exception ]    [ Gate Pass ]   [ Gate Fail ]
             │               │               │
             ▼               ▼               ▼
        ( FAILED )      ( PROMOTED )    ( REJECTED )
```

---

## 3. Automated Test Suite Proof (`tests/pytest/test_phase7_async_retraining.py`)

- `test_training_job_initialization`: Verifies job creation and `QUEUED` initial state.
- `test_job_failure_preserves_active_model`: Verifies transition to `FAILED` and active model preservation on error.
- `test_promotion_rejection_preserves_active_model`: Verifies transition to `REJECTED` when promotion criteria fails.

```bash
# Execution verification
python -m pytest tests/pytest/test_phase7_async_retraining.py -v
```
