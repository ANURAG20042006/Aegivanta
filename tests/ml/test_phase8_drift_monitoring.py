import pytest
import numpy as np
from ml.monitoring.drift_detector import AccumulatedWindowDriftDetector


def test_reference_distribution_and_window_accumulation():
    """Requirement 1 & 2 Proof: Baseline reference setup and accumulated window (no drift from single sample)."""
    np.random.seed(42)
    baseline = np.random.normal(loc=0.0, scale=1.0, size=(100, 4))
    detector = AccumulatedWindowDriftDetector(min_window_size=30, reference_version="ref-v1.0")
    detector.update_baseline(baseline, ["f1", "f2", "f3", "f4"])

    # Adding single observation returns None (does NOT evaluate drift from 1 sample)
    single_res = detector.add_observation(np.random.normal(0, 1, (1, 4)))
    assert single_res is None


def test_no_drift_on_matching_distribution():
    """Requirement 3 Proof: Matching production distribution produces NO_DRIFT status."""
    np.random.seed(42)
    baseline = np.random.normal(loc=0.0, scale=1.0, size=(200, 4))
    detector = AccumulatedWindowDriftDetector(min_window_size=50)
    detector.update_baseline(baseline, ["f1", "f2", "f3", "f4"])

    res = None
    for i in range(50):
        vec = baseline[i:i+1]
        res = detector.add_observation(vec, predicted_class="BENIGN")

    assert res is not None
    assert res["alert_status"] == "NO_DRIFT"
    assert len(res["drift_types"]) == 0
    assert res["sample_count"] == 50


def test_data_drift_detection_on_shifted_features():
    """Requirement 4 Proof: Detects DATA_DRIFT when input feature distribution shifts (KS & PSI)."""
    np.random.seed(42)
    baseline = np.random.normal(loc=0.0, scale=1.0, size=(200, 4))
    detector = AccumulatedWindowDriftDetector(min_window_size=50, psi_threshold=0.25, ks_alpha=0.05)
    detector.update_baseline(baseline, ["f1", "f2", "f3", "f4"])

    # Feed shifted feature distribution (mean shifted to 5.0)
    res = None
    for _ in range(50):
        shifted_vec = np.random.normal(loc=5.0, scale=1.0, size=(1, 4))
        res = detector.add_observation(shifted_vec, predicted_class="BENIGN")

    assert res is not None
    assert "DATA_DRIFT" in res["drift_types"]
    assert res["statistics"]["affected_features_count"] > 0
    assert res["alert_status"] in ["WARNING", "CRITICAL"]


def test_prediction_drift_detection_on_class_shift():
    """Requirement 4 & 5 Proof: Detects PREDICTION_DRIFT when predicted class distributions shift."""
    np.random.seed(42)
    baseline = np.random.normal(loc=0.0, scale=1.0, size=(200, 4))
    baseline_preds = ["BENIGN"] * 180 + ["DDoS"] * 20
    detector = AccumulatedWindowDriftDetector(min_window_size=50)
    detector.update_baseline(baseline, ["f1", "f2", "f3", "f4"], baseline_predictions=baseline_preds)

    # Feed production window with heavy attack shift (90% DDoS)
    res = None
    for i in range(50):
        vec = np.random.normal(loc=0.0, scale=1.0, size=(1, 4))
        pred_cls = "DDoS" if i < 45 else "BENIGN"
        res = detector.add_observation(vec, predicted_class=pred_cls)

    assert res is not None
    assert "PREDICTION_DRIFT" in res["drift_types"]
    assert "DDoS" in res["statistics"]["prediction_distribution_change"]


def test_concept_drift_performance_decay():
    """Requirement 5 Proof: Separate performance monitoring mechanism for CONCEPT_DRIFT with labels."""
    np.random.seed(42)
    baseline = np.random.normal(loc=0.0, scale=1.0, size=(200, 4))
    detector = AccumulatedWindowDriftDetector(min_window_size=20)
    detector.update_baseline(baseline, ["f1", "f2", "f3", "f4"])

    # Feed predictions with wrong ground-truth (simulating performance degradation / concept drift)
    res = None
    for _ in range(20):
        vec = np.random.normal(loc=0.0, scale=1.0, size=(1, 4))
        res = detector.add_observation(vec, predicted_class="BENIGN", ground_truth="DDoS")

    assert res is not None
    assert "CONCEPT_DRIFT" in res["drift_types"]
    assert res["alert_status"] == "CRITICAL"
    assert res["statistics"]["performance_metrics"]["accuracy"] == 0.0
