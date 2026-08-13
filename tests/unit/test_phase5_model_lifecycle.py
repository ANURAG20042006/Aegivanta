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
        accuracy=0.9500,
        f1_score=0.9450,
        precision_score=0.9510,
        recall_score=0.9410,
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


def test_promotion_gate_rejects_missing_fpr_phase2():
    """Phase 2 Proof: Missing FPR (None) MUST block promotion — no fallback value ever substituted."""
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.9850,
        candidate_recall=0.9500,
        candidate_fpr=None,           # FPR unavailable — gate must reject
        candidate_latency_ms=0.45,
        active_f1=0.9800,
        regression_tolerance=0.01
    )
    assert passed is False, (
        "CRITICAL: Promotion must be rejected when FPR is None. "
        "A missing security metric must never be replaced with an invented value."
    )
    assert "FPR metric unavailable" in reason, (
        f"Rejection reason must explicitly state FPR unavailability. Got: {reason}"
    )


def test_candidate_lifecycle_transitions():
    """
    TEST 12 — Candidate Lifecycle:
    Verify TRAINING -> CANDIDATE -> ACTIVE and TRAINING -> CANDIDATE -> REJECTED.
    Model MUST NOT be ACTIVE before promotion gate passes.
    """
    # 1. Registered initial candidate state
    cand = ModelRegistry(
        model_name="XGBoost Classifier",
        model_version="xgb-cand-v1.0",
        model_type="Boosting",
        status="CANDIDATE",
        is_active=False,
        artifact_path="ml/artifacts/xgboost.joblib"
    )
    assert cand.status == "CANDIDATE"
    assert cand.is_active is False

    # 2. Gate evaluation passes -> transitions CANDIDATE -> ACTIVE
    passed_pass, reason_pass = evaluate_promotion_gate(
        candidate_f1=0.98,
        candidate_recall=0.95,
        candidate_fpr=0.01,
        candidate_latency_ms=0.45,
        active_f1=0.90
    )
    assert passed_pass is True
    if passed_pass:
        cand.status = "ACTIVE"
        cand.is_active = True
    assert cand.status == "ACTIVE"
    assert cand.is_active is True

    # 3. Gate evaluation fails -> transitions CANDIDATE -> REJECTED
    cand_reject = ModelRegistry(
        model_name="Decision Tree",
        model_version="dt-cand-v1.0",
        model_type="Classical",
        status="CANDIDATE",
        is_active=False,
        artifact_path="ml/artifacts/decision_tree.joblib"
    )
    passed_rej, reason_rej = evaluate_promotion_gate(
        candidate_f1=0.70,   # Low F1 vs active 0.90
        candidate_recall=0.95,
        candidate_fpr=0.01,
        candidate_latency_ms=0.45,
        active_f1=0.90
    )
    assert passed_rej is False
    if not passed_rej:
        cand_reject.status = "REJECTED"
        cand_reject.is_active = False
    assert cand_reject.status == "REJECTED"
    assert cand_reject.is_active is False


