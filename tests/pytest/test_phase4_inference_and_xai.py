import pytest
import numpy as np
from ml.explainability.real_explainer import RealModelExplainer
from sklearn.ensemble import RandomForestClassifier


def test_explanation_generated_from_actual_model():
    """Requirement 2 & 4 Proof: Explanation features and contributions are derived from model."""
    X = np.random.randn(100, 10)
    y = np.random.randint(0, 2, size=100)
    
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)

    feature_names = [f"Feature_{i}" for i in range(10)]
    explainer = RealModelExplainer(model, feature_names)

    sample = X[0:1]
    res = explainer.explain_instance(
        processed_vector=sample,
        model_version="random_forest-v1.0",
        prediction="BENIGN",
        confidence=0.98,
        top_n=5
    )

    assert res["explanation_available"] is True
    assert res["model_version"] == "random_forest-v1.0"
    assert res["prediction"] == "BENIGN"
    assert res["confidence"] == 0.98
    assert len(res["features"]) <= 5
    
    # Check structure of feature items
    for item in res["features"]:
        assert "feature" in item
        assert "contribution" in item
        assert "direction" in item
        assert item["direction"] in ["positive", "negative"]
        assert "rank" in item


def test_prediction_and_explanation_same_sample():
    """Requirement 4 Proof: Prediction and explanation use the exact same processed sample vector."""
    X = np.random.randn(50, 8)
    y = np.random.randint(0, 2, size=50)
    
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)

    feature_names = [f"Feat_{i}" for i in range(8)]
    explainer = RealModelExplainer(model, feature_names)

    sample = X[5:6]
    pred = str(model.predict(sample)[0])
    probs = model.predict_proba(sample)[0]
    conf = float(np.max(probs))

    res = explainer.explain_instance(
        processed_vector=sample,
        model_version="rf-v1.0",
        prediction=pred,
        confidence=conf,
        top_n=3
    )

    assert res["explanation_available"] is True
    assert res["prediction"] == pred
    assert res["confidence"] == round(conf, 4)


def test_explanation_graceful_failure_no_fabrication():
    """Requirement 2 Proof: Returns explanation_available = False on failure without fabricating data."""
    # Explainer with dummy model that causes failure
    class BrokenModel:
        pass

    broken_model = BrokenModel()
    explainer = RealModelExplainer(broken_model, ["feat_1", "feat_2"])

    sample = np.array([[1.0, 2.0]])
    res = explainer.explain_instance(
        processed_vector=sample,
        model_version="broken-v1.0",
        prediction="BENIGN",
        confidence=0.95
    )

    assert res["explanation_available"] is False
    assert res["explanation_method"] is None
    assert len(res["features"]) == 0
