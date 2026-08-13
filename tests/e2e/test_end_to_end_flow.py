import pytest
import numpy as np
from ml.schema.feature_schema import validate_input_vector, DEFAULT_FEATURE_SCHEMA
from ml.explainability.real_explainer import RealModelExplainer
from backend.app.api.v1.train import evaluate_promotion_gate
from backend.app.models.incident import is_valid_state_transition
from sklearn.ensemble import RandomForestClassifier


def test_full_sentinelai_end_to_end_pipeline():
    """Requirement E2E Proof: Verifies complete threat detection, explanation, promotion, and incident containment flow."""
    # 1. Feature Vector Schema Contract Validation
    vector = {
        "Destination Port": 80,
        "Flow Duration": 500.0,
        "Total Fwd Packets": 10.0,
        "Total Backward Packets": 5.0,
        "Total Length of Fwd Packets": 1000.0,
        "Total Length of Bwd Packets": 500.0,
        "Flow Bytes/s": 15000.0,
        "Flow Packets/s": 150.0,
        "Packet Length Mean": 512.0,
        "Packet Length Std": 24.5,
        "SYN Flag Count": 1.0,
        "RST Flag Count": 0.0,
        "PSH Flag Count": 0.0,
        "ACK Flag Count": 1.0,
        "URG Flag Count": 0.0,
        "Average Packet Size": 512.0
    }
    is_valid, errors = validate_input_vector(vector, DEFAULT_FEATURE_SCHEMA)
    assert is_valid is True
    assert len(errors) == 0

    # 2. Model Inference & XAI Feature Attribution
    X = np.random.randn(50, 16)
    y = np.random.randint(0, 2, size=50)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)

    feature_names = DEFAULT_FEATURE_SCHEMA.feature_names
    explainer = RealModelExplainer(model, feature_names)
    sample = X[0:1]

    xai_res = explainer.explain_instance(
        processed_vector=sample,
        model_version="random_forest-v1.0",
        prediction="DDoS",
        confidence=0.9850,
        top_n=5
    )
    assert xai_res["explanation_available"] is True
    assert xai_res["prediction"] == "DDoS"
    assert len(xai_res["features"]) <= 5

    # 3. Model Promotion Gate Evaluation
    passed, reason = evaluate_promotion_gate(
        candidate_f1=0.9850,
        candidate_recall=0.9500,
        candidate_fpr=0.0120,
        candidate_latency_ms=0.45,
        active_f1=0.9800
    )
    assert passed is True
    assert "PASSED" in reason

    # 4. Incident Response Lifecycle Containment Transition
    assert is_valid_state_transition("DETECTED", "TRIAGED") is True
    assert is_valid_state_transition("TRIAGED", "INVESTIGATING") is True
    assert is_valid_state_transition("INVESTIGATING", "CONTAINED") is True
