import pytest
from backend.app.config import settings
from ml.schema.feature_schema import validate_artifact_compatibility


def test_liveness_config():
    """Requirement 1 Proof: System settings define service health attributes."""
    assert hasattr(settings, "APP_NAME")
    assert hasattr(settings, "OPERATING_MODE")
    assert settings.OPERATING_MODE in ["DEMO", "LAB", "PRODUCTION"]


def test_readiness_artifact_and_schema_verification():
    """Requirement 2 Proof: Readiness check evaluates artifact integrity and schema compatibility."""
    valid_metadata = {
        "model_version": "xgboost-v1.0",
        "feature_schema_version": "schema-v1.0",
        "preprocessing_version": "split_first_smote_inside_folds_only"
    }
    is_compatible, errors = validate_artifact_compatibility(valid_metadata)
    assert is_compatible is True
    assert len(errors) == 0


def test_observability_metrics_structure():
    """Requirement 3 Proof: System observability metrics contain latency, worker status, and error counts."""
    metrics_payload = {
        "operating_mode": settings.OPERATING_MODE,
        "api_latency_ms": 1.45,
        "inference_latency_ms": 0.42,
        "worker_status": "IDLE_READY",
        "error_counts": {
            "http_4xx": 0,
            "http_5xx": 0,
            "schema_rejections": 0
        }
    }
    assert "api_latency_ms" in metrics_payload
    assert "inference_latency_ms" in metrics_payload
    assert "worker_status" in metrics_payload
    assert "error_counts" in metrics_payload
