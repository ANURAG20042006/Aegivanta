import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


def get_authenticated_headers(username: str = "admin", password: str = None) -> dict:
    if password is None:
        env_map = {
            "admin": "SENTINEL_ADMIN_PASSWORD",
            "analyst": "SENTINEL_ANALYST_PASSWORD",
            "viewer": "SENTINEL_VIEWER_PASSWORD"
        }
        password = os.getenv(env_map.get(username, "SENTINEL_ADMIN_PASSWORD"), "TestAdminPassword2026!")
    response = client.post("/api/v1/auth/login", data={"username": username, "password": password})
    if response.status_code == 200:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    return {}


def test_alerts_pipeline_and_triage():
    analyst_hdr = get_authenticated_headers("analyst")
    viewer_hdr = get_authenticated_headers("viewer")

    # 1. Trigger a flow prediction to generate an alert
    flow_payload = {
        "features": {
            "source_ip": "198.51.100.44",
            "destination_ip": "10.0.0.5",
            "source_port": 54321,
            "destination_port": 80,
            "protocol": "TCP",
            "flow_duration": 999999.0,
            "flow_packets_s": 5000.0,
            "packet_length_mean": 1400.0,
            "syn_flag_count": 1.0
        },
        "model_name": "Random Forest"
    }
    pred_res = client.post(
        "/api/v1/predict/single",
        json=flow_payload,
        headers=analyst_hdr
    )
    assert pred_res.status_code == 200

    # 2. Query alerts list
    alerts_res = client.get("/api/v1/alerts", headers=viewer_hdr)
    assert alerts_res.status_code == 200
    data = alerts_res.json()
    assert "items" in data
    assert "total" in data

    # 3. Query alert stats
    stats_res = client.get("/api/v1/alerts/summary/stats", headers=viewer_hdr)
    assert stats_res.status_code == 200
    stats_data = stats_res.json()
    assert "total_active_alerts" in stats_data
    assert "severity_breakdown" in stats_data

    # 4. Status updates
    if len(data["items"]) > 0:
        target_alert = data["items"][0]
        alert_id = target_alert["id"]

        # Viewer cannot update status -> 403
        res_viewer_update = client.patch(
            f"/api/v1/alerts/{alert_id}/status",
            json={"status": "acknowledged", "notes": "Viewer attempt"},
            headers=viewer_hdr
        )
        assert res_viewer_update.status_code == 403

        # Analyst updates status -> 200 OK
        res_analyst_update = client.patch(
            f"/api/v1/alerts/{alert_id}/status",
            json={"status": "acknowledged", "notes": "Triage started by analyst"},
            headers=analyst_hdr
        )
        assert res_analyst_update.status_code == 200
        assert res_analyst_update.json()["status"] == "acknowledged"
