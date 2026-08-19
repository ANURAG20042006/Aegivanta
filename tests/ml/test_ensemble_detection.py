"""
tests/ml/test_ensemble_detection.py
===================================
Unit & integration tests for Phase 2 Multi-Model Ensemble Detection and Confidence Calibration.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.ensemble_service import (
    EnsembleThreatDetector,
    EnsembleStrategy,
    ConfidenceCalibrator
)

client = TestClient(app)


def test_confidence_calibrator():
    """Verify temperature scaling calibration is smooth and bounded in [0, 1]."""
    # Over-confident raw 0.99 should soften with T=1.15
    raw = 0.99
    cal = ConfidenceCalibrator.calibrate(raw, temperature=1.15)
    assert 0.0 < cal < 1.0
    assert cal < raw  # Softened

    # Edge cases
    assert ConfidenceCalibrator.calibrate(0.0) == 0.0
    assert ConfidenceCalibrator.calibrate(1.0) == 1.0


def test_ensemble_hard_voting():
    """Verify Hard Voting majority resolution and model agreement percentage."""
    detector = EnsembleThreatDetector()
    sample_preds = {
        "CatBoost": ("DDoS", 0.96, {"DDoS": 0.96, "BENIGN": 0.04}),
        "LightGBM": ("DDoS", 0.94, {"DDoS": 0.94, "BENIGN": 0.06}),
        "Random Forest": ("Port Scan", 0.70, {"Port Scan": 0.70, "DDoS": 0.30}),
        "Decision Tree": ("DDoS", 0.85, {"DDoS": 0.85, "BENIGN": 0.15}),
        "XGBoost": ("DDoS", 0.95, {"DDoS": 0.95, "BENIGN": 0.05}),
    }

    res = detector.aggregate_predictions(sample_preds, strategy=EnsembleStrategy.HARD_VOTING)
    assert res["final_prediction"] == "DDoS"
    assert res["is_malicious"] is True
    assert res["model_agreement_pct"] == 80.0  # 4 out of 5 voted DDoS
    assert res["ensemble_strategy"] == EnsembleStrategy.HARD_VOTING


def test_ensemble_weighted_confidence():
    """Verify Weighted Confidence strategy incorporates model weights."""
    detector = EnsembleThreatDetector()
    detector.model_weights = {"ModelA": 0.9, "ModelB": 0.1}

    sample_preds = {
        "ModelA": ("DDoS", 0.90, {"DDoS": 0.90, "BENIGN": 0.10}),
        "ModelB": ("BENIGN", 0.60, {"BENIGN": 0.60, "DDoS": 0.40}),
    }

    res = detector.aggregate_predictions(sample_preds, strategy=EnsembleStrategy.WEIGHTED_CONFIDENCE)
    assert res["final_prediction"] == "DDoS"
    assert res["is_malicious"] is True
    assert "calibrated_confidence" in res
    assert res["total_models_evaluated"] == 2


def test_live_ensemble_inference_api():
    """Integration test: submit live network flow to /api/v1/predict/single with model_name='Ensemble'."""
    from tests.integration.test_complete_soc_pipeline import get_auth_headers
    analyst_hdr = get_auth_headers("analyst")

    flow_payload = {
        "features": {
            "source_ip": "198.51.100.99",
            "destination_ip": "10.0.0.1",
            "source_port": 50100,
            "destination_port": 80,
            "protocol": "TCP",
            "flow_duration": 5000000.0,
            "total_fwd_packets": 1000.0,
            "total_backward_packets": 0.0,
            "total_length_of_fwd_packets": 500000.0,
            "flow_packets_s": 10000.0,
            "packet_length_mean": 500.0,
            "fwd_header_length": 40000.0,
            "syn_flag_count": 1.0,
            "min_packet_length": 40.0,
            "max_packet_length": 1460.0
        },
        "model_name": "Ensemble"
    }

    res = client.post("/api/v1/predict/single", json=flow_payload, headers=analyst_hdr)
    assert res.status_code == 200, f"Ensemble prediction failed: {res.text}"
    data = res.json()
    assert data["model_used"] == "Ensemble"
    assert "attack_type" in data
    assert "is_malicious" in data
    assert data["confidence_available"] is True
    assert "shap_explanation" in data
    assert "model_agreement_pct" in data["shap_explanation"]
    assert "individual_predictions" in data["shap_explanation"]
    assert "CatBoost" in data["shap_explanation"]["individual_predictions"]
    assert "LightGBM" in data["shap_explanation"]["individual_predictions"]
