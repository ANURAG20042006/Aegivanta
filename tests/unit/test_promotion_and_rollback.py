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
