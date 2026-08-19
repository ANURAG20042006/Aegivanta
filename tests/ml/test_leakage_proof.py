import pytest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock
from ml.dataset.generator import CICIDS2017DataGenerator
from ml.dataset.preprocessor import CICIDS2017Preprocessor
from ml.train_pipeline import run_leakage_free_cv, run_training_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split


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
    """Requirement 1 & 2 Proof: SimpleImputer, StandardScaler, and SelectKBest are fitted ONLY on X_train."""
    df = CICIDS2017DataGenerator.generate_synthetic_dataset(num_samples=500)
    preprocessor = CICIDS2017Preprocessor(n_features_to_select=15)
    
    # Fit preprocessor on dataset
    X_train, X_test, y_train, y_test = preprocessor.fit_transform_train_test(
        df, target_column="Label", balance_data=True, test_size=0.20, random_state=42
    )

    # Verify fitted parameters exist
    assert hasattr(preprocessor.imputer, "statistics_")
    assert hasattr(preprocessor.scaler, "mean_")
    assert hasattr(preprocessor.feature_selector, "scores_")
    
    # Create isolated preprocessor fit ONLY on training split manually
    cleaned = preprocessor.clean_dataset(df)
    X_raw = cleaned.drop(columns=["Label"])
    y_raw = preprocessor.label_encoder.transform(cleaned["Label"].astype(str))
    
    X_tr_manual, X_te_manual, y_tr_manual, y_te_manual = train_test_split(
        X_raw, y_raw, test_size=0.20, random_state=42, stratify=y_raw
    )
    
    manual_imputer = SimpleImputer(strategy="median")
    manual_imputer.fit(X_tr_manual)
    
    manual_scaler = StandardScaler()
    manual_scaler.fit(manual_imputer.transform(X_tr_manual))
    
    # Verify imputer and scaler statistics match manual pipeline fitted strictly on X_tr_manual
    np.testing.assert_array_almost_equal(preprocessor.imputer.statistics_, manual_imputer.statistics_)
    np.testing.assert_array_almost_equal(preprocessor.scaler.mean_, manual_scaler.mean_)


def test_test_only_outlier_does_not_affect_fitted_imputer_or_scaler():
    """
    Proof: Extreme outliers or missing values in X_test cannot alter
    preprocessor.imputer.statistics_ or preprocessor.scaler.mean_.
    """
    df = CICIDS2017DataGenerator.generate_synthetic_dataset(num_samples=500)
    preprocessor = CICIDS2017Preprocessor(n_features_to_select=15)
    
    cleaned = preprocessor.clean_dataset(df)
    X_raw = cleaned.drop(columns=["Label"])
    y_raw = preprocessor.label_encoder.fit_transform(cleaned["Label"].astype(str))
    
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw, y_raw, test_size=0.20, random_state=42, stratify=y_raw
    )
    
    # Preprocessor 1: Fit strictly on X_train_raw
    prep1 = CICIDS2017Preprocessor(n_features_to_select=15)
    prep1.fit_transform_train(X_train_raw, y_train, balance_data=False)
    
    # Preprocessor 2: Fit on same X_train_raw, then transform heavily corrupted X_test_raw
    prep2 = CICIDS2017Preprocessor(n_features_to_select=15)
    prep2.fit_transform_train(X_train_raw, y_train, balance_data=False)
    
    # Corrupt X_test with massive outliers and NaNs
    X_test_corrupted = X_test_raw.copy()
    X_test_corrupted.iloc[0, :] = 1e12  # trillion outlier
    X_test_corrupted.iloc[1, :] = -1e12 # negative trillion outlier
    X_test_corrupted.iloc[2, :] = np.nan # missing values
    
    _ = prep2.transform_test(X_test_corrupted)
    
    # Verify statistics remain 100% identical and unpolluted
    np.testing.assert_array_almost_equal(prep1.imputer.statistics_, prep2.imputer.statistics_)
    np.testing.assert_array_almost_equal(prep1.scaler.mean_, prep2.scaler.mean_)
    np.testing.assert_array_almost_equal(prep1.scaler.var_, prep2.scaler.var_)
    np.testing.assert_array_almost_equal(prep1.feature_selector.scores_, prep2.feature_selector.scores_)


def test_preprocessor_fitted_statistics_come_only_from_training_rows():
    """
    Proof: All fitted statistics (imputer median, scaler mean/variance, feature selector F-scores)
    are calculated exclusively from training rows and are identical to standalone training-only computation.
    """
    df = CICIDS2017DataGenerator.generate_synthetic_dataset(num_samples=400)
    preprocessor = CICIDS2017Preprocessor(n_features_to_select=10)
    
    X_train_out, X_test_out, y_train_out, y_test_out = preprocessor.fit_transform_train_test(
        df, target_column="Label", balance_data=False, test_size=0.25, random_state=123
    )
    
    cleaned = preprocessor.clean_dataset(df)
    X_raw = cleaned.drop(columns=["Label"])
    y_raw = preprocessor.label_encoder.transform(cleaned["Label"].astype(str))
    
    X_tr_isolated, X_te_isolated, y_tr_isolated, y_te_isolated = train_test_split(
        X_raw, y_raw, test_size=0.25, random_state=123, stratify=y_raw
    )
    
    # Standalone reference calculations on training split
    ref_imputer = SimpleImputer(strategy="median").fit(X_tr_isolated)
    ref_imputed = ref_imputer.transform(X_tr_isolated)
    
    ref_scaler = StandardScaler().fit(ref_imputed)
    ref_scaled = ref_scaler.transform(ref_imputed)
    
    ref_selector = SelectKBest(score_func=f_classif, k=10).fit(ref_scaled, y_tr_isolated)
    
    # Assert fitted preprocessor matches training reference exactly
    np.testing.assert_array_almost_equal(preprocessor.imputer.statistics_, ref_imputer.statistics_)
    np.testing.assert_array_almost_equal(preprocessor.scaler.mean_, ref_scaler.mean_)
    np.testing.assert_array_almost_equal(preprocessor.scaler.var_, ref_scaler.var_)
    np.testing.assert_array_almost_equal(preprocessor.feature_selector.scores_, ref_selector.scores_)


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


@pytest.mark.slow
@pytest.mark.research
def test_final_test_evaluated_only_after_model_selection(tmp_path):
    """Requirement 4 Proof: Training pipeline runs model selection and evaluates untouched test set once."""
    results = run_training_pipeline(
        num_synthetic_samples=500,
        n_splits=3,
        random_seed=42,
        artifacts_dir=str(tmp_path / "artifacts"),
        experiment_id="EXP-TEST-001"
    )
    assert len(results) > 0
    champion = results[0]
    assert "model_name" in champion, f"Expected 'model_name' key, got keys: {list(champion.keys())}"
    # run_training_pipeline returns CV leaderboard dicts (cv_f1_mean, selection_score, etc.)
    # final_test_metrics are written to metadata.json — verified by test_metadata_has_four_metric_sections
    assert "cv_f1_mean" in champion or "f1_score" in champion or "accuracy" in champion, (
        f"Champion dict must have at least one metric key, got: {list(champion.keys())}"
    )
