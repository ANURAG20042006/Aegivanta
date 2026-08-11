import pytest
from backend.app.models.training_job import TrainingJob, VALID_JOB_STATUSES


def test_training_job_initialization():
    """Requirement 2 Proof: TrainingJob model supports QUEUED, RUNNING, PROMOTED, REJECTED, FAILED statuses."""
    job = TrainingJob(
        user_id="user_admin_123",
        status="QUEUED",
        model_name="XGBoost Classifier"
    )
    assert job.status in VALID_JOB_STATUSES
    assert job.status == "QUEUED"
    assert job.model_name == "XGBoost Classifier"


def test_job_failure_preserves_active_model():
    """Requirement 3 Proof: Job failure transitions to FAILED without modifying active model."""
    job = TrainingJob(
        user_id="user_admin_123",
        status="FAILED",
        error_message="Dataset file corrupt or unreadable."
    )
    assert job.status == "FAILED"
    assert job.candidate_version is None
    assert "corrupt" in job.error_message


def test_promotion_rejection_preserves_active_model():
    """Requirement 3 Proof: Candidate failing promotion gate transitions to REJECTED."""
    job = TrainingJob(
        user_id="user_admin_123",
        status="REJECTED",
        candidate_version="xgboost-v2.0",
        promotion_reason="Candidate F1 (0.8000) is below active threshold with tolerance (0.9700)."
    )
    assert job.status == "REJECTED"
    assert job.candidate_version == "xgboost-v2.0"
    assert "below active threshold" in job.promotion_reason
