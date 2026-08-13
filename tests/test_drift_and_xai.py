import pytest
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from ml.explainability.real_explainer import RealModelExplainer
from ml.monitoring.drift_detector import AccumulatedWindowDriftDetector


class DummyLinearModel:
    def predict(self, X):
        return np.zeros(len(X))


def test_xai_supported_tree_model():
    X_train = np.random.normal(0, 1, size=(50, 5))
    y_train = np.random.randint(0, 2, size=50)
    model = RandomForestClassifier(n_estimators=5, random_state=42)
    model.fit(X_train, y_train)

    feature_names = [f"feat_{i}" for i in range(5)]
    explainer = RealModelExplainer(model=model, feature_names=feature_names)

    vector = np.array([1.2, 0.5, 3.4, 0.0, 2.1])
    result = explainer.explain_instance(
        processed_vector=vector,
        model_version="random_forest_v1.0",
        prediction="DoS Hulk",
        confidence=0.92,
        top_n=3
    )

    assert result["available"] is True
    assert result["reason"] is None
    assert result["model_version"] == "random_forest_v1.0"
    assert result["prediction"] == "DoS Hulk"
    assert result["confidence"] == 0.92
    assert "xai_latency_ms" in result
    assert isinstance(result["xai_latency_ms"], float)
    assert len(result["top_features"]) <= 3
    for feat in result["top_features"]:
        assert "feature" in feat
        assert "input_value" in feat
        assert "contribution" in feat
        assert "rank" in feat
        assert feat["direction"] in ["positive", "negative", "POSITIVE", "NEGATIVE"]


def test_xai_unsupported_model_returns_honest_failure():
    model = DummyLinearModel()
    feature_names = ["feat_1", "feat_2"]
    explainer = RealModelExplainer(model=model, feature_names=feature_names)

    vector = np.array([1.0, 2.0])
    result = explainer.explain_instance(
        processed_vector=vector,
        model_version="linear_v1.0",
        prediction="BENIGN",
        confidence=None
    )

    assert result["available"] is False
    assert "not supported" in result["reason"].lower()
    assert result["top_features"] == []
    assert "xai_latency_ms" in result


def test_drift_detector_normal_distribution():
    np.random.seed(42)
    baseline = np.random.normal(loc=0.0, scale=1.0, size=(500, 5))
    feature_names = [f"f_{i}" for i in range(5)]

    detector = AccumulatedWindowDriftDetector(
        reference_version="ref-1.0",
        baseline_distribution=baseline,
        feature_names=feature_names,
        min_window_size=100
    )

    # Feed 100 observations sampled from the SAME distribution
    eval_result = None
    for _ in range(100):
        obs = np.random.normal(loc=0.0, scale=1.0, size=5)
        res = detector.add_observation(obs, predicted_class="BENIGN")
        if res is not None:
            eval_result = res

    assert eval_result is not None
    assert eval_result["status"] == "NORMAL"
    assert eval_result["statistics"]["affected_features_count"] == 0
    assert eval_result["retraining_recommended"] is False


def test_drift_detector_known_distribution_shift():
    np.random.seed(42)
    baseline = np.random.normal(loc=0.0, scale=1.0, size=(500, 5))
    feature_names = [f"f_{i}" for i in range(5)]

    detector = AccumulatedWindowDriftDetector(
        reference_version="ref-1.0",
        baseline_distribution=baseline,
        feature_names=feature_names,
        min_window_size=100,
        psi_threshold=0.25
    )

    # Feed 100 observations sampled from a SIGNIFICANTLY SHIFTED distribution (mean=5.0)
    eval_result = None
    for _ in range(100):
        obs = np.random.normal(loc=5.0, scale=1.0, size=5)
        res = detector.add_observation(obs, predicted_class="DDoS")
        if res is not None:
            eval_result = res

    assert eval_result is not None
    assert eval_result["status"] == "DRIFT_DETECTED"
    assert eval_result["statistics"]["affected_features_count"] > 0
    assert eval_result["retraining_recommended"] is True


def test_drift_detector_constant_features():
    baseline = np.ones((100, 3))
    feature_names = ["const_1", "const_2", "const_3"]

    detector = AccumulatedWindowDriftDetector(
        reference_version="ref-const",
        baseline_distribution=baseline,
        feature_names=feature_names,
        min_window_size=50
    )

    eval_result = None
    for _ in range(50):
        obs = np.ones(3)
        res = detector.add_observation(obs)
        if res is not None:
            eval_result = res

    assert eval_result is not None
    assert eval_result["status"] == "NORMAL"


def test_drift_detector_small_window_returns_none():
    baseline = np.random.normal(0, 1, size=(100, 4))
    detector = AccumulatedWindowDriftDetector(
        baseline_distribution=baseline,
        min_window_size=50
    )

    # Add only 49 observations
    for _ in range(49):
        res = detector.add_observation(np.random.normal(0, 1, size=4))
        assert res is None
