import pytest
import os
import joblib
from pathlib import Path
from backend.app.api.v1.train import evaluate_promotion_gate, verify_rollback_artifact_integrity
from backend.app.models.model_registry import ModelRegistry


def test_1_missing_latency_rejects_promotion():
    """TEST 1 — Missing latency: candidate_latency_ms = None -> REJECT with reason containing 'latency unavailable'."""
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.98,
        candidate_recall=0.95,
        candidate_fpr=0.01,
        candidate_latency_ms=None,  # missing latency
        active_f1=0.92
    )
    assert passed is False
    assert "latency unavailable" in reason


def test_2_excessive_latency_rejects_promotion():
    """TEST 2 — Excessive latency: candidate_latency_ms > configured maximum (5.0ms) -> REJECT."""
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.98,
        candidate_recall=0.95,
        candidate_fpr=0.01,
        candidate_latency_ms=12.50,  # exceeds 5.0ms limit
        active_f1=0.92
    )
    assert passed is False
    assert "exceeds max limit" in reason or "latency" in reason


def test_3_per_class_regression_accepted():
    """TEST 3 — Per-class regression accepted: Active DDoS recall = 0.90, Candidate DDoS recall = 0.89, Tolerance = 0.02 -> PASS."""
    active_per_class = {
        "BENIGN": {"precision": 0.98, "recall": 0.98, "f1": 0.98},
        "DDoS": {"precision": 0.92, "recall": 0.90, "f1": 0.91}
    }
    candidate_per_class = {
        "BENIGN": {"precision": 0.98, "recall": 0.98, "f1": 0.98},
        "DDoS": {"precision": 0.92, "recall": 0.89, "f1": 0.90}  # 0.89 >= 0.90 - 0.02 (0.88) -> PASS
    }
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.94,
        candidate_recall=0.935,
        candidate_fpr=0.01,
        candidate_latency_ms=0.45,
        active_f1=0.94,
        regression_tolerance=0.02,
        active_per_class_metrics=active_per_class,
        candidate_per_class_metrics=candidate_per_class
    )
    assert passed is True, f"Expected PASS for 0.89 vs 0.90 with 0.02 tolerance. Reason: {reason}"
    assert "PASSED" in reason


def test_4_per_class_regression_rejected():
    """TEST 4 — Per-class regression rejected: Active DDoS recall = 0.90, Candidate DDoS recall = 0.87, Tolerance = 0.02 -> REJECT."""
    active_per_class = {
        "BENIGN": {"precision": 0.98, "recall": 0.98, "f1": 0.98},
        "DDoS": {"precision": 0.92, "recall": 0.90, "f1": 0.91}
    }
    candidate_per_class = {
        "BENIGN": {"precision": 0.98, "recall": 0.98, "f1": 0.98},
        "DDoS": {"precision": 0.92, "recall": 0.87, "f1": 0.89}  # 0.87 < 0.90 - 0.02 (0.88) -> REJECT
    }
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.94,
        candidate_recall=0.925,
        candidate_fpr=0.01,
        candidate_latency_ms=0.45,
        active_f1=0.94,
        regression_tolerance=0.02,
        active_per_class_metrics=active_per_class,
        candidate_per_class_metrics=candidate_per_class
    )
    assert passed is False
    assert "Promotion rejected: DDoS recall regressed from 0.90 to 0.87, exceeding tolerance 0.02." in reason


def test_5_multiple_classes_evaluated():
    """TEST 5 — Multiple classes: Candidate fails if Macro F1 improves but one class regresses beyond tolerance."""
    active_per_class = {
        "BENIGN": {"precision": 0.90, "recall": 0.90, "f1": 0.90},
        "PortScan": {"precision": 0.88, "recall": 0.92, "f1": 0.90},
        "Infiltration": {"precision": 0.85, "recall": 0.88, "f1": 0.86}
    }
    # Macro F1 improves overall, but Infiltration recall drops 0.88 -> 0.80 (tolerance 0.02)
    candidate_per_class = {
        "BENIGN": {"precision": 0.99, "recall": 0.99, "f1": 0.99},
        "PortScan": {"precision": 0.95, "recall": 0.95, "f1": 0.95},
        "Infiltration": {"precision": 0.85, "recall": 0.80, "f1": 0.82}  # regressed 0.88 -> 0.80
    }
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.95,   # Macro F1 improved vs active 0.88
        candidate_recall=0.91,
        candidate_fpr=0.01,
        candidate_latency_ms=0.45,
        active_f1=0.88,
        regression_tolerance=0.02,
        active_per_class_metrics=active_per_class,
        candidate_per_class_metrics=candidate_per_class
    )
    assert passed is False, "Must reject promotion when one class regresses despite aggregate Macro F1 improvement"
    assert "Infiltration" in reason
    assert "regressed" in reason


def test_6_missing_per_class_metrics_rejects():
    """TEST 6 — Missing per-class metrics: Required per-class metrics unavailable -> REJECT."""
    active_per_class = {
        "BENIGN": {"recall": 0.95},
        "DDoS": {"recall": 0.90}
    }
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.98,
        candidate_recall=0.95,
        candidate_fpr=0.01,
        candidate_latency_ms=0.45,
        active_f1=0.90,
        active_per_class_metrics=active_per_class,
        candidate_per_class_metrics=None  # missing candidate per-class metrics
    )
    assert passed is False
    assert "per-class metrics unavailable" in reason


def test_7_class_mismatch_rejects():
    """TEST 7 — Class mismatch: Candidate and active models have incompatible class sets -> REJECT."""
    active_per_class = {
        "BENIGN": {"recall": 0.95},
        "DDoS": {"recall": 0.90}
    }
    candidate_per_class = {
        "BENIGN": {"recall": 0.95},
        "Botnet": {"recall": 0.90}  # Botnet instead of DDoS
    }
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.98,
        candidate_recall=0.95,
        candidate_fpr=0.01,
        candidate_latency_ms=0.45,
        active_f1=0.90,
        active_per_class_metrics=active_per_class,
        candidate_per_class_metrics=candidate_per_class
    )
    assert passed is False
    assert "does not match active model class set" in reason


def test_8_rollback_missing_artifact():
    """TEST 8 — Rollback missing artifact: Delete/point target artifact to nonexistent file -> rollback rejected."""
    target_model = ModelRegistry(
        model_name="Random Forest",
        model_version="rf-v999.0",
        model_type="Classical",
        status="ARCHIVED",
        artifact_path="ml/artifacts/nonexistent_model_file_12345.joblib"
    )
    ok, err_msg = verify_rollback_artifact_integrity(target_model)
    assert ok is False
    assert "does not exist" in err_msg


def test_9_rollback_corrupted_artifact(tmp_path):
    """TEST 9 — Rollback corrupted artifact: Create invalid/corrupted artifact -> rollback rejected."""
    corrupt_file = tmp_path / "corrupt_model.joblib"
    corrupt_file.write_bytes(b"INVALID_HEADER_NOT_A_JOBLIB_FILE")

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


class DummyModelForTest:
    def __init__(self):
        self.n_features_in_ = 999  # Model expects 999 features, preprocessor produces 30

    def predict(self, X):
        return [0]


def test_10_rollback_incompatible_schema(tmp_path):
    """TEST 10 — Rollback incompatible schema: Model feature count mismatch -> rollback rejected."""
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
    assert "expects 999 features" in err_msg or "schema" in err_msg or "features" in err_msg


def test_11_successful_rollback_artifact_integrity():
    """TEST 11 — Successful rollback artifact integrity: Valid target model -> validation passes."""
    artifacts_dir = Path("ml/artifacts")
    model_file = artifacts_dir / "random_forest.joblib"
    if not model_file.exists():
        model_file = artifacts_dir / "best_model.joblib"
    assert model_file.exists(), "Model artifact must exist in ml/artifacts"

    target_model = ModelRegistry(
        model_name="Random Forest",
        model_version="random_forest-v1.0",
        model_type="Classical",
        status="ARCHIVED",
        artifact_path=str(model_file)
    )
    ok, msg = verify_rollback_artifact_integrity(target_model)
    assert ok is True, f"Expected successful rollback artifact verification, got: {msg}"
    assert "PASSED" in msg

