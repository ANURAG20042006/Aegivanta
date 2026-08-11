import pytest
import json
from pathlib import Path
from ml.schema.feature_schema import (
    DEFAULT_FEATURE_SCHEMA,
    validate_input_vector,
    validate_artifact_compatibility
)


def test_valid_vector():
    """Test 1: Valid vector with all required features in valid range."""
    valid_sample = {
        "Destination Port": 80.0,
        "Flow Duration": 1200.0,
        "Flow Packets/s": 500.0,
        "Packet Length Mean": 450.0,
        "SYN Flag Count": 1.0
    }
    is_valid, errors = validate_input_vector(valid_sample, DEFAULT_FEATURE_SCHEMA)
    assert is_valid is True
    assert len(errors) == 0


def test_missing_feature():
    """Test 2: Vector missing a required feature ('Flow Packets/s')."""
    sample = {
        "Destination Port": 80.0,
        "Flow Duration": 1200.0,
        "Packet Length Mean": 450.0
    }
    is_valid, errors = validate_input_vector(sample, DEFAULT_FEATURE_SCHEMA)
    assert is_valid is False
    assert any("Missing required feature" in err for err in errors)


def test_extra_feature():
    """Test 3: Vector containing extra optional features is supported."""
    sample = {
        "Destination Port": 80.0,
        "Flow Duration": 1200.0,
        "Flow Packets/s": 500.0,
        "Packet Length Mean": 450.0,
        "SYN Flag Count": 1.0,
        "custom_extra_feature": 999.0
    }
    is_valid, errors = validate_input_vector(sample, DEFAULT_FEATURE_SCHEMA)
    assert is_valid is True


def test_reordered_feature():
    """Test 4: Vector with reordered feature keys is validated correctly."""
    sample = {
        "SYN Flag Count": 1.0,
        "Packet Length Mean": 450.0,
        "Flow Packets/s": 500.0,
        "Flow Duration": 1200.0,
        "Destination Port": 80.0
    }
    is_valid, errors = validate_input_vector(sample, DEFAULT_FEATURE_SCHEMA)
    assert is_valid is True


def test_invalid_dtype():
    """Test 5: Feature with invalid data type (e.g. dictionary or list)."""
    sample = {
        "Destination Port": 80.0,
        "Flow Duration": {"invalid": "nested_dict"},
        "Flow Packets/s": 500.0,
        "Packet Length Mean": 450.0,
        "SYN Flag Count": 1.0
    }
    is_valid, errors = validate_input_vector(sample, DEFAULT_FEATURE_SCHEMA)
    assert is_valid is False
    assert any("Invalid data type" in err for err in errors)


def test_invalid_range():
    """Test 6: Feature value outside allowed numerical range."""
    sample = {
        "Destination Port": 999999.0,  # Max allowed is 65535.0
        "Flow Duration": 1200.0,
        "Flow Packets/s": 500.0,
        "Packet Length Mean": 450.0,
        "SYN Flag Count": 1.0
    }
    is_valid, errors = validate_input_vector(sample, DEFAULT_FEATURE_SCHEMA)
    assert is_valid is False
    assert any("out of allowed range" in err for err in errors)


def test_schema_mismatch():
    """Test 7: Metadata with incompatible feature schema version."""
    invalid_metadata = {
        "model_version": "xgboost-v1.0",
        "feature_schema_version": "schema-v9.9-incompatible",
        "preprocessing_version": "split_first_smote_inside_folds_only"
    }
    ok, errors = validate_artifact_compatibility(invalid_metadata)
    assert ok is False
    assert any("Incompatible feature schema version" in err for err in errors)


def test_missing_model_version():
    """Test 8: Metadata missing model version."""
    invalid_metadata = {
        "feature_schema_version": "schema-v1.0",
        "preprocessing_version": "split_first_smote_inside_folds_only"
    }
    ok, errors = validate_artifact_compatibility(invalid_metadata)
    assert ok is False
    assert any("Model version missing" in err for err in errors)


def test_corrupted_artifact():
    """Test 9: Metadata empty or corrupted."""
    ok, errors = validate_artifact_compatibility({})
    assert ok is False
    assert any("missing or empty" in err for err in errors)


def test_incompatible_preprocessing_version():
    """Test 10: Metadata with unsupported preprocessing pipeline version."""
    invalid_metadata = {
        "model_version": "xgboost-v1.0",
        "feature_schema_version": "schema-v1.0",
        "preprocessing_version": "global_leakage_smote_before_cv"
    }
    ok, errors = validate_artifact_compatibility(invalid_metadata)
    assert ok is False
    assert any("Incompatible preprocessing version" in err for err in errors)
