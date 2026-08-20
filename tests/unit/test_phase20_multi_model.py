import pytest
from backend.app.services.multi_model_detection_service import MultiModelDetectionService


def test_multi_model_benign_traffic():
    features = {
        "flow_duration": 1500.0,
        "tot_fwd_pkts": 12.0,
        "flow_bytes_s": 420.0,
        "fwd_pkt_len_mean": 64.0
    }
    res = MultiModelDetectionService.execute_multi_model_inference(features)
    assert res["prediction"] == "BENIGN"
    assert res["is_malicious"] is False
    assert res["severity"] == "INFORMATIONAL"
    assert "components" in res
    assert "xai" in res
    assert len(res["xai"]["contributing_signals"]) > 0


def test_multi_model_ddos_detection_and_xai():
    features = {
        "flow_duration": 80.0,
        "tot_fwd_pkts": 850.0,
        "flow_bytes_s": 65000.0,
        "fwd_pkt_len_mean": 950.0
    }
    res = MultiModelDetectionService.execute_multi_model_inference(features, entity_id="HOST-TEST-99")
    assert res["prediction"] == "DDoS_LOIC"
    assert res["is_malicious"] is True
    assert res["severity"] in ["HIGH", "CRITICAL"]
    assert res["confidence"] >= 0.70
    assert "Multi-Model Ensemble" in res["xai"]["reasoning_summary"]
    # Check SHAP-like attribution weights sum to ~1.0
    weights_sum = sum(s["importance_weight"] for s in res["xai"]["contributing_signals"])
    assert 0.95 <= weights_sum <= 1.05
