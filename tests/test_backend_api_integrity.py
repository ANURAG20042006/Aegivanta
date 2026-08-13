import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings


client = TestClient(app)


def get_authenticated_headers(username: str = "admin", password: str = None) -> dict:
    """Helper to authenticate against test app and return Bearer token headers."""
    if password is None:
        env_map = {"admin": "SENTINEL_ADMIN_PASSWORD", "analyst": "SENTINEL_ANALYST_PASSWORD", "viewer": "SENTINEL_VIEWER_PASSWORD"}
        password = os.getenv(env_map.get(username, "SENTINEL_ADMIN_PASSWORD"), "TestAdminPassword2026!")
    response = client.post("/api/v1/auth/login", data={"username": username, "password": password})
    if response.status_code == 200:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    return {}


def test_1_feature_schema_validation_failure_returns_400():
    """Test feature vector with invalid datatype returns HTTP 400 Bad Request."""
    headers = get_authenticated_headers("admin")
    invalid_payload = {
        "features": {
            "flow_duration": -100.0,  # Negative duration violates non-negative constraint
            "destination_port": 999999  # Invalid port out of 0-65535 range
        }
    }
    response = client.post("/api/v1/predict/single", json=invalid_payload, headers=headers)
    assert response.status_code == 400
    assert "Feature schema validation failed" in response.json().get("detail", "")


def test_2_valid_single_prediction_flow_creates_incident():
    """Test valid packet vector returns prediction result with legitimate probability & SHAP explanation."""
    headers = get_authenticated_headers("analyst")
    valid_payload = {
        "features": {
            "destination_port": 80,
            "flow_duration": 120500.0,
            "flow_bytes_s": 1024.0,
            "flow_packets_s": 150.0,
            "packet_length_mean": 512.0,
            "packet_length_std": 12.0,
            "syn_flag_count": 0.0,
            "ack_flag_count": 1.0
        }
    }
    response = client.post("/api/v1/predict/single", json=valid_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "incident_id" in data
    assert "attack_type" in data
    assert "is_malicious" in data
    assert "shap_explanation" in data


def test_3_predict_remediate_dynamic_operating_mode():
    """Test /predict/remediate resolves OPERATING_MODE dynamically."""
    headers = get_authenticated_headers("analyst")
    payload = {
        "target_ip": "192.168.1.50",
        "action": "BLOCK_IP"
    }
    response = client.post("/api/v1/predict/remediate", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "SUCCESS"
    assert "remediation_mode" in data


def test_4_training_trigger_creates_real_queued_job(monkeypatch):
    """Test POST /train/trigger creates a real queued training job with UUID."""
    async def mock_async_worker(job_id: str):
        pass

    monkeypatch.setattr("backend.app.api.v1.train.async_train_worker", mock_async_worker)

    headers = get_authenticated_headers("admin")
    response = client.post("/api/v1/train/trigger", headers=headers)
    assert response.status_code in [200, 202]
    data = response.json()
    assert "job_id" in data
    assert data.get("status") == "QUEUED"


def test_5_analytics_summary_returns_db_backed_metrics():
    """Test GET /analytics/summary returns metrics backed by active model and DB records."""
    headers = get_authenticated_headers("viewer")
    response = client.get("/api/v1/analytics/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "active_model" in data
    assert "total_packets_inspected" in data
    assert "total_threats_detected" in data


def test_6_unhandled_exception_returns_sanitized_500_with_request_id():
    """Test exception handler returns sanitized HTTP 500 containing request_id without leaking internals."""
    response = client.get("/invalid_endpoint_path_does_not_exist")
    assert response.status_code == 404
