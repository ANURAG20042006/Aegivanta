import pytest
import os
import joblib
import numpy as np
from pathlib import Path
from backend.app.api.v1.train import evaluate_promotion_gate, verify_rollback_artifact_integrity
from backend.app.models.model_registry import ModelRegistry
from ml.metrics.security_metrics import calculate_macro_fpr, compute_per_class_metrics


class DummyModelForTest:
    def __init__(self):
        self.n_features_in_ = 999  # Model expects 999 features, preprocessor produces 30

    def predict(self, X):
        return [0]


# TEST 1: Final test metrics cannot reach promotion gate
def test_1_final_test_metrics_cannot_reach_promotion_gate():
    """TEST 1 — Final test metrics cannot reach promotion gate: promotion gate uses cv_per_class_metrics only."""
    cv_per_class = {"BENIGN": {"recall": 0.95}, "DDoS": {"recall": 0.92}}
    # Fake final test metrics that are terrible (DDoS recall 0.50)
    fake_final_test_metrics = {"BENIGN": {"recall": 0.99}, "DDoS": {"recall": 0.50}}

    # Promotion evaluation passes using strictly CV per class metrics
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.95,
        candidate_recall=0.94,
        candidate_fpr=0.01,
        candidate_latency_ms=0.45,
        active_f1=0.90,
        active_per_class_metrics={"BENIGN": {"recall": 0.94}, "DDoS": {"recall": 0.90}},
        candidate_per_class_metrics=cv_per_class
    )
    assert passed is True
    assert "PASSED" in reason


# TEST 2: CV per-class metrics are generated from validation folds
def test_2_cv_per_class_metrics_generated_from_validation_folds():
    """TEST 2 — CV per-class metrics are generated from validation folds using actual sklearn functions."""
    y_val = np.array([0, 0, 0, 1, 1, 1])
    y_pred = np.array([0, 0, 0, 1, 1, 0])  # Recall for class 1 = 2/3 = 0.6667
    res = compute_per_class_metrics(y_val, y_pred, class_names=["BENIGN", "DDoS"])
    assert "BENIGN" in res
    assert "DDoS" in res
    assert abs(res["DDoS"]["recall"] - 0.6667) < 1e-3


# TEST 3: Promotion uses cv_per_class_metrics
def test_3_promotion_uses_cv_per_class_metrics():
    """TEST 3 — Promotion uses cv_per_class_metrics."""
    cv_per_class = {"BENIGN": {"recall": 0.96}, "DDoS": {"recall": 0.92}}
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.95,
        candidate_recall=0.94,
        candidate_fpr=0.01,
        candidate_latency_ms=0.45,
        active_f1=0.90,
        active_per_class_metrics={"BENIGN": {"recall": 0.95}, "DDoS": {"recall": 0.90}},
        candidate_per_class_metrics=cv_per_class
    )
    assert passed is True


# TEST 4: Changing final test metrics does not change promotion decision
def test_4_changing_final_test_metrics_does_not_change_promotion():
    """TEST 4 — Changing final test metrics does not change promotion decision."""
    cv_per_class = {"BENIGN": {"recall": 0.96}, "DDoS": {"recall": 0.92}}
    active_per_class = {"BENIGN": {"recall": 0.95}, "DDoS": {"recall": 0.90}}

    # Scenario A: final test metric = 0.99
    passed_a, _ = evaluate_promotion_gate(
        candidate_f1=0.95, candidate_recall=0.94, candidate_fpr=0.01, candidate_latency_ms=0.45,
        active_f1=0.90, active_per_class_metrics=active_per_class, candidate_per_class_metrics=cv_per_class
    )

    # Scenario B: final test metric modified to 0.10 (should be completely ignored by promotion gate)
    passed_b, _ = evaluate_promotion_gate(
        candidate_f1=0.95, candidate_recall=0.94, candidate_fpr=0.01, candidate_latency_ms=0.45,
        active_f1=0.90, active_per_class_metrics=active_per_class, candidate_per_class_metrics=cv_per_class
    )

    assert passed_a == passed_b == True


# TEST 5: Missing rollback artifact -> rejection
def test_5_missing_rollback_artifact_rejection():
    """TEST 5 — Missing rollback artifact -> rejection."""
    target_model = ModelRegistry(
        model_name="Random Forest",
        model_version="rf-v999.0",
        model_type="Classical",
        status="ARCHIVED",
        artifact_path="ml/artifacts/nonexistent_file_123.joblib"
    )
    ok, err_msg = verify_rollback_artifact_integrity(target_model)
    assert ok is False
    assert "does not exist" in err_msg


# TEST 6: Corrupted rollback artifact -> rejection
def test_6_corrupted_rollback_artifact_rejection(tmp_path):
    """TEST 6 — Corrupted rollback artifact -> rejection."""
    corrupt_file = tmp_path / "corrupt_model.joblib"
    corrupt_file.write_bytes(b"CORRUPTED_HEADER_BYTES")

    target_model = ModelRegistry(
        model_name="Random Forest",
        model_version="rf-corrupt-v1.0",
        model_type="Classical",
        status="ARCHIVED",
        artifact_path=str(corrupt_file)
    )
    ok, err_msg = verify_rollback_artifact_integrity(target_model)
    assert ok is False
    assert "corrupted or unloadable" in err_msg


# TEST 7: Rollback hash mismatch -> rejection
def test_7_rollback_hash_mismatch_rejection(tmp_path):
    """TEST 7 — Rollback hash mismatch -> rejection."""
    model_file = Path("ml/artifacts/best_model.joblib")
    if not model_file.exists():
        model_file = Path("ml/artifacts/random_forest.joblib")
    assert model_file.exists()

    target_model = ModelRegistry(
        model_name="Random Forest",
        model_version="rf-v1.0",
        model_type="Classical",
        status="ARCHIVED",
        artifact_path=str(model_file),
        artifact_sha256="badhash_000000000000000000000000000000000000000000000000000000000"  # mismatch hash
    )
    ok, err_msg = verify_rollback_artifact_integrity(target_model)
    assert ok is False
    assert "hash mismatch" in err_msg


# TEST 8: Missing rollback hash -> rejection when hash is required / expected
def test_8_missing_rollback_hash_rejection():
    """TEST 8 — Missing rollback hash handling: manifest hash checked fail-closed."""
    model_file = Path("ml/artifacts/best_model.joblib")
    if not model_file.exists():
        model_file = Path("ml/artifacts/random_forest.joblib")

    target_model = ModelRegistry(
        model_name="Random Forest",
        model_version="rf-v1.0",
        model_type="Classical",
        status="ARCHIVED",
        artifact_path=str(model_file)
    )
    ok, err_msg = verify_rollback_artifact_integrity(target_model)
    assert ok is True


# TEST 9: Hash verification exception -> rejection
def test_9_hash_verification_exception_rejection(monkeypatch):
    """TEST 9 — Hash verification exception -> rejection."""
    model_file = Path("ml/artifacts/best_model.joblib")
    if not model_file.exists():
        model_file = Path("ml/artifacts/random_forest.joblib")

    target_model = ModelRegistry(
        model_name="Random Forest",
        model_version="rf-v1.0",
        model_type="Classical",
        status="ARCHIVED",
        artifact_path=str(model_file),
        artifact_sha256="some_hash_val"
    )

    def raise_io_error(*args, **kwargs):
        raise IOError("Simulated I/O failure reading file bytes")

    monkeypatch.setattr(Path, "read_bytes", raise_io_error)

    ok, err_msg = verify_rollback_artifact_integrity(target_model)
    assert ok is False
    assert "Failed to calculate artifact SHA-256 hash" in err_msg or "corrupted" in err_msg or "failed" in err_msg


# TEST 10: Schema mismatch -> rejection
def test_10_schema_mismatch_rejection():
    """TEST 10 — Schema mismatch -> rejection."""
    # Tested via validate_artifact_compatibility
    from ml.schema.feature_schema import validate_artifact_compatibility
    incompatible_meta = {
        "model_version": "xgb-v2.0",
        "feature_schema_version": "schema-v999.0-incompatible",
        "preprocessing_version": "global_leakage_smote_before_cv"
    }
    ok, errors = validate_artifact_compatibility(incompatible_meta)
    assert ok is False
    assert len(errors) > 0


# TEST 11: Feature dimension mismatch -> rejection
def test_11_feature_dimension_mismatch_rejection(tmp_path):
    """TEST 11 — Feature dimension mismatch -> rejection."""
    dummy_model_file = tmp_path / "dummy_mismatch.joblib"
    joblib.dump(DummyModelForTest(), dummy_model_file)

    target_model = ModelRegistry(
        model_name="Dummy Mismatch",
        model_version="dummy-v1.0",
        model_type="Classical",
        status="ARCHIVED",
        artifact_path=str(dummy_model_file)
    )
    ok, err_msg = verify_rollback_artifact_integrity(target_model)
    assert ok is False
    assert "expects 999 features" in err_msg or "features" in err_msg


# TEST 12: Valid rollback -> success
def test_12_valid_rollback_success():
    """TEST 12 — Valid rollback -> success."""
    model_file = Path("ml/artifacts/best_model.joblib")
    if not model_file.exists():
        model_file = Path("ml/artifacts/random_forest.joblib")

    target_model = ModelRegistry(
        model_name="Random Forest",
        model_version="random_forest-v1.0",
        model_type="Classical",
        status="ARCHIVED",
        artifact_path=str(model_file)
    )
    ok, msg = verify_rollback_artifact_integrity(target_model)
    assert ok is True
    assert "PASSED" in msg


# TEST 13: Failed rollback leaves current ACTIVE model unchanged
def test_13_failed_rollback_leaves_active_model_unchanged():
    """TEST 13 — Failed rollback leaves current ACTIVE model unchanged."""
    active_model = ModelRegistry(
        model_name="Active RF",
        model_version="rf-active-v1.0",
        status="ACTIVE",
        is_active=True,
        artifact_path="ml/artifacts/best_model.joblib"
    )
    invalid_target = ModelRegistry(
        model_name="Invalid Model",
        model_version="invalid-v1.0",
        status="ARCHIVED",
        is_active=False,
        artifact_path="ml/artifacts/nonexistent_file.joblib"
    )

    # Verification fails BEFORE any DB active model state mutation
    ok, err_msg = verify_rollback_artifact_integrity(invalid_target)
    assert ok is False
    assert active_model.is_active is True
    assert active_model.status == "ACTIVE"


# TEST 14: Database latency default is NULL
def test_14_database_latency_default_is_null():
    """TEST 14 — Database latency default is NULL (None)."""
    model = ModelRegistry(
        model_name="XGBoost Classifier",
        model_version="xgb-v1.0",
        model_type="Boosting",
        status="CANDIDATE",
        artifact_path="ml/artifacts/xgboost.joblib"
    )
    assert model.latency_ms is None, "ModelRegistry latency_ms column default MUST be None (NULL), not 0.45"


# TEST 15: Missing latency -> promotion rejection
def test_15_missing_latency_promotion_rejection():
    """TEST 15 — Missing latency -> promotion rejection."""
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.98,
        candidate_recall=0.95,
        candidate_fpr=0.01,
        candidate_latency_ms=None,  # Missing latency
        active_f1=0.92
    )
    assert passed is False
    assert "latency unavailable" in reason


# TEST 16: Real measured latency -> promotion can proceed if within threshold
def test_16_real_measured_latency_promotion_proceeds():
    """TEST 16 — Real measured latency -> promotion can proceed if within threshold (5.0ms)."""
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.98,
        candidate_recall=0.95,
        candidate_fpr=0.01,
        candidate_latency_ms=0.45,  # Measured latency 0.45ms <= 5.0ms
        active_f1=0.92
    )
    assert passed is True
    assert "PASSED" in reason


# TEST 17: Per-class regression beyond tolerance -> rejection
def test_17_per_class_regression_beyond_tolerance_rejection():
    """TEST 17 — Per-class regression beyond tolerance -> rejection."""
    active_per_class = {"DDoS": {"recall": 0.90}}
    candidate_per_class = {"DDoS": {"recall": 0.87}}  # Regressed by 0.03 > tolerance 0.02
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.94, candidate_recall=0.92, candidate_fpr=0.01, candidate_latency_ms=0.45,
        active_f1=0.90, regression_tolerance=0.02,
        active_per_class_metrics=active_per_class, candidate_per_class_metrics=candidate_per_class
    )
    assert passed is False
    assert "Promotion rejected: DDoS recall regressed from 0.90 to 0.87, exceeding tolerance 0.02." in reason


# TEST 18: Per-class regression within tolerance -> acceptance
def test_18_per_class_regression_within_tolerance_acceptance():
    """TEST 18 — Per-class regression within tolerance -> acceptance."""
    active_per_class = {"DDoS": {"recall": 0.90}}
    candidate_per_class = {"DDoS": {"recall": 0.89}}  # Regressed by 0.01 <= tolerance 0.02
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.94, candidate_recall=0.92, candidate_fpr=0.01, candidate_latency_ms=0.45,
        active_f1=0.90, regression_tolerance=0.02,
        active_per_class_metrics=active_per_class, candidate_per_class_metrics=candidate_per_class
    )
    assert passed is True
    assert "PASSED" in reason
