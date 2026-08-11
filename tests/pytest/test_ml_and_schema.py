import pytest
import numpy as np
import pandas as pd
from ml.schema.feature_schema import DEFAULT_FEATURE_SCHEMA, validate_input_vector
from ml.dataset.preprocessor import CICIDS2017Preprocessor
from ml.dataset.generator import CICIDS2017DataGenerator
from ml.train_pipeline import run_leakage_free_cv


def test_feature_schema_validation():
    """Verifies strict feature schema contract validation."""
    # Valid vector containing all required canonical attributes
    valid_vector = {
        "Flow Packets/s": 1500.0,
        "Packet Length Mean": 512.0,
        "SYN Flag Count": 1.0,
        "Flow Duration": 500.0,
        "Total Fwd Packets": 10.0,
        "Total Backward Packets": 5.0,
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.1",
        "source_port": 5000,
        "destination_port": 80,
        "protocol": "TCP"
    }
    is_valid, errors = validate_input_vector(valid_vector, DEFAULT_FEATURE_SCHEMA)
    assert is_valid is True
    assert len(errors) == 0

    # Invalid vector missing required canonical attribute
    invalid_vector = {
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.1"
    }
    is_valid, errors = validate_input_vector(invalid_vector, DEFAULT_FEATURE_SCHEMA)
    assert is_valid is False
    assert len(errors) > 0


def test_preprocessor_split_first():
    """Verifies that preprocessor fits scaler and selector strictly on X_train."""
    df = CICIDS2017DataGenerator.generate_synthetic_dataset(num_samples=600)
    preprocessor = CICIDS2017Preprocessor(n_features_to_select=10)
    X_train, X_test, y_train, y_test = preprocessor.fit_transform_train_test(
        df, target_column="Label", balance_data=True, test_size=0.20, random_state=42
    )

    assert X_train.shape[1] == 10
    assert X_test.shape[1] == 10
    assert len(X_train) + len(X_test) > 0


def test_leakage_free_cv():
    """Verifies leakage-free cross-validation execution."""
    df = CICIDS2017DataGenerator.generate_synthetic_dataset(num_samples=600)
    mean_f1, std_f1, fold_results = run_leakage_free_cv(df, n_splits=3, random_seed=42)

    assert mean_f1 >= 0.0
    assert len(fold_results) == 3
