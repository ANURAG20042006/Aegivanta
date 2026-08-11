import pytest
from backend.app.api.v1.train import evaluate_promotion_gate
from backend.app.models.model_registry import ModelRegistry, VALID_MODEL_STATUSES


def test_model_registry_statuses():
    """Requirement 1 Proof: ModelRegistry supports versioned lifecycle statuses."""
    model = ModelRegistry(
        model_name="XGBoost Classifier",
        model_version="xgboost-v1.0",
        model_type="Boosting",
        status="CANDIDATE",
        accuracy=0.9912,
        f1_score=0.9901,
        precision_score=0.9920,
        recall_score=0.9882,
        latency_ms=0.42,
        is_active=False,
        artifact_path="ml/artifacts/xgboost.joblib"
    )
    assert model.status in VALID_MODEL_STATUSES
    assert model.model_version == "xgboost-v1.0"
    assert model.is_active is False


def test_promotion_gate_multi_metric_eval():
    """Requirement 2 Proof: Promotion gate evaluates multi-metric criteria and regression tolerance."""
    # 1. Candidate passes all multi-metric thresholds -> PASS
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.9850,
        candidate_recall=0.9500,
        candidate_fpr=0.0120,
        candidate_latency_ms=0.45,
        active_f1=0.9800,
        regression_tolerance=0.01,
        artifact_metadata={
            "model_version": "xgb-v2.0",
            "feature_schema_version": "schema-v1.0",
            "preprocessing_version": "split_first_smote_inside_folds_only"
        }
    )
    assert passed is True
    assert "PASSED" in reason

    # 2. Candidate F1 drops significantly beyond regression tolerance -> REJECT
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.9000,
        candidate_recall=0.9500,
        candidate_fpr=0.0120,
        candidate_latency_ms=0.45,
        active_f1=0.9800,
        regression_tolerance=0.01
    )
    assert passed is False
    assert "below active threshold" in reason

    # 3. Candidate Latency exceeds 5.0ms -> REJECT
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.9850,
        candidate_recall=0.9500,
        candidate_fpr=0.0120,
        candidate_latency_ms=12.50,
        active_f1=0.9800
    )
    assert passed is False
    assert "exceeds max limit" in reason


def test_artifact_compatibility_in_promotion():
    """Requirement 2 Proof: Promotion gate checks schema version and preprocessing compatibility."""
    incompatible_meta = {
        "model_version": "xgb-v2.0",
        "feature_schema_version": "schema-v9.9-incompatible",
        "preprocessing_version": "global_leakage_smote_before_cv"
    }
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.9900,
        candidate_recall=0.9800,
        candidate_fpr=0.0100,
        artifact_metadata=incompatible_meta
    )
    assert passed is False
    assert "Schema Compatibility Failed" in reason
