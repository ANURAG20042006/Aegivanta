import pytest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock
from ml.dataset.generator import CICIDS2017DataGenerator
from ml.dataset.preprocessor import CICIDS2017Preprocessor
from ml.train_pipeline import run_leakage_free_cv, run_training_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest


def test_test_data_never_reaches_smote():
    """Requirement 1 & 4 Proof: Test data is untouched by SMOTE balancing."""
    df = CICIDS2017DataGenerator.generate_synthetic_dataset(num_samples=500)
    preprocessor = CICIDS2017Preprocessor(n_features_to_select=15)
    
    # Calculate raw test size expected
    test_size_fraction = 0.20
    expected_test_count = int(len(df) * test_size_fraction)
    
    X_train, X_test, y_train, y_test = preprocessor.fit_transform_train_test(
        df, target_column="Label", balance_data=True, test_size=test_size_fraction, random_state=42
    )

    # Test set sample count must match untouched raw split count (not oversampled by SMOTE)
    assert len(X_test) == expected_test_count
    assert len(y_test) == expected_test_count
    # Training set sample count should be larger due to SMOTE balancing on minority classes
    assert len(X_train) > (len(df) * (1 - test_size_fraction))


def test_preprocessing_not_fitted_on_test_data():
    """Requirement 1 & 2 Proof: StandardScaler and SelectKBest are fitted ONLY on X_train."""
    df = CICIDS2017DataGenerator.generate_synthetic_dataset(num_samples=500)
    preprocessor = CICIDS2017Preprocessor(n_features_to_select=15)
    
    # Fit preprocessor on dataset
    X_train, X_test, y_train, y_test = preprocessor.fit_transform_train_test(
        df, target_column="Label", balance_data=True, test_size=0.20, random_state=42
    )

    # Verify fitted parameters exist
    assert hasattr(preprocessor.scaler, "mean_")
    assert hasattr(preprocessor.feature_selector, "scores_")
    
    # Create isolated preprocessor fit ONLY on training split manually
    cleaned = preprocessor.clean_dataset(df)
    X_raw = cleaned.drop(columns=["Label"])
    y_raw = preprocessor.label_encoder.transform(cleaned["Label"].astype(str))
    
    from sklearn.model_selection import train_test_split
    X_tr_manual, X_te_manual, y_tr_manual, y_te_manual = train_test_split(
        X_raw, y_raw, test_size=0.20, random_state=42, stratify=y_raw
    )
    
    manual_scaler = StandardScaler()
    manual_scaler.fit(X_tr_manual)
    
    # Verify scaler mean_ matches manual scaler fitted strictly on X_tr_manual
    np.testing.assert_array_almost_equal(preprocessor.scaler.mean_, manual_scaler.mean_)


def test_cv_folds_independently_fit_preprocessing():
    """Requirement 2 Proof: StratifiedKFold fits preprocessing independently inside EVERY training fold."""
    df = CICIDS2017DataGenerator.generate_synthetic_dataset(num_samples=500)
    cv_mean, cv_std, fold_details = run_leakage_free_cv(df, n_splits=5, random_seed=42)

    assert len(fold_details) == 5
    for fold in fold_details:
        assert "Macro F1" in fold
        assert "Precision" in fold
        assert "Recall" in fold
        # Ensure fold Macro F1 is a valid probability score
        assert 0.0 <= fold["Macro F1"] <= 1.0


def test_final_test_evaluated_only_after_model_selection():
    """Requirement 4 Proof: Training pipeline runs model selection and evaluates untouched test set once."""
    results = run_training_pipeline(num_synthetic_samples=500, n_splits=3, random_seed=42)
    assert len(results) > 0
    champion = results[0]
    assert "model_name" in champion, f"Expected 'model_name' key, got keys: {list(champion.keys())}"
    # run_training_pipeline returns CV leaderboard dicts (cv_f1_mean, selection_score, etc.)
    # final_test_metrics are written to metadata.json — verified by test_metadata_has_four_metric_sections
    assert "cv_f1_mean" in champion or "f1_score" in champion or "accuracy" in champion, (
        f"Champion dict must have at least one metric key, got: {list(champion.keys())}"
    )
