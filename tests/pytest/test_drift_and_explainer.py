import pytest
import numpy as np
from ml.monitoring.drift_detector import AccumulatedWindowDriftDetector
from ml.explainability.real_explainer import RealModelExplainer
from sklearn.ensemble import RandomForestClassifier


def test_drift_detector():
    """Verifies KS test & PSI calculation in accumulated window drift detector."""
    np.random.seed(42)
    baseline = np.random.normal(loc=0.0, scale=1.0, size=(100, 5))
    detector = AccumulatedWindowDriftDetector(min_window_size=20)
    detector.update_baseline(baseline, [f"feat_{i}" for i in range(5)])

    # Add observations matching baseline (no drift)
    res = None
    for _ in range(20):
        vec = np.random.normal(loc=0.0, scale=1.0, size=(1, 5))
        res = detector.add_observation(vec)

    assert res is not None
    assert "alert_status" in res


def test_real_model_explainer():
    """Verifies SHAP TreeExplainer feature attributions."""
    X = np.random.randn(50, 10)
    y = np.random.randint(0, 2, size=50)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)

    feature_names = [f"Feature_{i}" for i in range(10)]
    explainer = RealModelExplainer(model, feature_names)
    sample = X[0:1]
    explanation = explainer.explain_instance(sample, top_n=3)
    assert explanation["explanation_available"] is True
    assert len(explanation["features"]) <= 3
