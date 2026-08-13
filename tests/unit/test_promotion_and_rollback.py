import pytest
from backend.app.api.v1.train import evaluate_promotion_gate


def test_promotion_gate_evaluation():
    """Verifies multi-metric promotion gate evaluation logic."""
    # 1. Candidate satisfies all criteria -> PASS
    passed, reason = evaluate_promotion_gate(candidate_f1=0.98, candidate_recall=0.95, candidate_fpr=0.01, active_f1=0.92)
    assert passed is True
    assert "PASSED" in reason

    # 2. Candidate F1 lower than active -> REJECT
    passed, reason = evaluate_promotion_gate(candidate_f1=0.80, candidate_recall=0.95, candidate_fpr=0.01, active_f1=0.92)
    assert passed is False
    assert "below active" in reason

    # 3. Candidate Recall below minimum 0.85 -> REJECT
    passed, reason = evaluate_promotion_gate(candidate_f1=0.95, candidate_recall=0.80, candidate_fpr=0.01, active_f1=0.90)
    assert passed is False
    assert "minimum threshold" in reason

    # 4. Candidate FPR exceeds 0.05 -> REJECT
    passed, reason = evaluate_promotion_gate(candidate_f1=0.95, candidate_recall=0.90, candidate_fpr=0.08, active_f1=0.90)
    assert passed is False
    assert "exceeds max allowed" in reason


def test_promotion_gate_rejects_missing_fpr():
    """Phase 2: A missing (None) FPR MUST block promotion. No fallback value is substituted."""
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.98,
        candidate_recall=0.95,
        candidate_fpr=None,   # missing metric
        active_f1=0.92
    )
    assert passed is False, "Promotion must be rejected when FPR is unavailable"
    assert "FPR metric unavailable" in reason, f"Rejection reason must state FPR unavailability, got: {reason}"


def test_promotion_gate_rejects_missing_f1():
    """Phase 2: A missing (None) Macro F1 MUST block promotion. No fallback value is substituted."""
    passed, reason = evaluate_promotion_gate(
        candidate_f1=None,   # missing metric
        candidate_recall=0.95,
        candidate_fpr=0.02,
        active_f1=0.92
    )
    assert passed is False, "Promotion must be rejected when F1 is unavailable"
    assert "F1 metric unavailable" in reason, f"Rejection reason must state F1 unavailability, got: {reason}"


def test_promotion_gate_rejects_missing_recall():
    """Phase 2: A missing (None) Recall MUST block promotion. No fallback value is substituted."""
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.98,
        candidate_recall=None,  # missing metric
        candidate_fpr=0.02,
        active_f1=0.92
    )
    assert passed is False, "Promotion must be rejected when Recall is unavailable"
    assert "Recall metric unavailable" in reason, f"Rejection reason must state Recall unavailability, got: {reason}"


def test_promotion_gate_fpr_boundary():
    """Phase 2: FPR boundary conditions — exactly at limit passes, one ULP above fails."""
    # FPR == 0.05 exactly -> PASS (within limit)
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.98, candidate_recall=0.90, candidate_fpr=0.05, active_f1=0.90
    )
    assert passed is True, f"FPR=0.05 (at limit) should pass. Got: {reason}"

    # FPR == 0.0501 -> REJECT (exceeds limit)
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.98, candidate_recall=0.90, candidate_fpr=0.0501, active_f1=0.90
    )
    assert passed is False, "FPR=0.0501 (above limit) should be rejected"
    assert "exceeds max allowed" in reason


def test_promotion_gate_all_none_metrics_reject():
    """Phase 2: All metrics None -> rejected on first unavailable metric (F1), not silently passed."""
    passed, reason = evaluate_promotion_gate(
        candidate_f1=None,
        candidate_recall=None,
        candidate_fpr=None,
        active_f1=0.90
    )
    assert passed is False
    assert "unavailable" in reason.lower()


def test_promotion_gate_no_hardcoded_fpr_fallback():
    """Phase 2: Confirm no fallback FPR value exists — None must always reject, not silently pass."""
    # If a fallback like 0.05 existed, this would pass. It must not.
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.98,
        candidate_recall=0.95,
        candidate_fpr=None,
        active_f1=0.85
    )
    assert passed is False, (
        "CRITICAL: Promotion must never use a hardcoded FPR fallback. "
        "A None FPR must always block promotion."
    )
