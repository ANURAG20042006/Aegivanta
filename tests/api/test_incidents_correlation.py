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


def test_incident_detail_timeline_and_notes():
    analyst_hdr = get_authenticated_headers("analyst")
    viewer_hdr = get_authenticated_headers("viewer")

    # 1. Trigger prediction to create an incident
    flow_payload = {
        "features": {
            "source_ip": "203.0.113.88",
            "destination_ip": "10.0.1.20",
            "source_port": 43210,
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
        "model_name": "LightGBM"
    }
    pred_res = client.post(
        "/api/v1/predict/single",
        json=flow_payload,
        headers=analyst_hdr
    )
    assert pred_res.status_code == 200
    incident_id = pred_res.json().get("incident_id")
    assert incident_id is not None

    # 2. Get Incident Detail with Timeline
    detail_res = client.get(
        f"/api/v1/incidents/{incident_id}",
        headers=viewer_hdr
    )
    assert detail_res.status_code == 200
    inc_data = detail_res.json()
    assert inc_data["id"] == incident_id
    assert "timeline" in inc_data
    assert "alerts" in inc_data
    assert len(inc_data["timeline"]) >= 1
    assert "risk_score" in inc_data

    # 3. Append analyst note to attack timeline
    note_payload = {
        "event_type": "ANALYST_ACTION",
        "title": "Threat Actor IP Investigation",
        "description": "Cross-referenced IP with threat intelligence database."
    }
    note_res = client.post(
        f"/api/v1/incidents/{incident_id}/timeline",
        json=note_payload,
        headers=analyst_hdr
    )
    assert note_res.status_code == 200
    assert note_res.json()["status"] == "SUCCESS"

    # 4. Progress lifecycle state: DETECTED -> TRIAGED -> INVESTIGATING
    triage_res = client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        json={"status": "TRIAGED", "notes": "Triaged by security analyst"},
        headers=analyst_hdr
    )
    assert triage_res.status_code == 200
    assert triage_res.json()["new_status"] == "TRIAGED"

    investigate_res = client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        json={"status": "INVESTIGATING", "notes": "Active deep dive in progress"},
        headers=analyst_hdr
    )
    assert investigate_res.status_code == 200
    assert investigate_res.json()["new_status"] == "INVESTIGATING"

    # 5. Execute remediation action
    remediate_res = client.post(
        f"/api/v1/incidents/{incident_id}/remediate",
        json={"action": "BLOCK_IP", "reason": "Active intrusion containment"},
        headers=analyst_hdr
    )
    assert remediate_res.status_code == 200
    assert remediate_res.json()["status"] == "SUCCESS"
    assert remediate_res.json()["current_status"] == "CONTAINED"

    # 6. Verify timeline now reflects all actions
    refreshed = client.get(
        f"/api/v1/incidents/{incident_id}",
        headers=viewer_hdr
    ).json()
    event_types = [evt["event_type"] for evt in refreshed["timeline"]]
    assert "DETECTION" in event_types
    assert "ANALYST_ACTION" in event_types
    assert "STATUS_CHANGE" in event_types
    assert "REMEDIATION" in event_types


def test_explicit_incident_severity_policy():
    """Test deterministic Incident Severity Policy rules."""
    from backend.app.services.correlation_engine import IncidentCorrelationEngine

    # 1. Alert severity higher than current -> escalates to alert severity
    assert IncidentCorrelationEngine.determine_incident_severity("Low", "Critical", 30.0) == "Critical"
    assert IncidentCorrelationEngine.determine_incident_severity("Medium", "High", 45.0) == "High"

    # 2. Risk score exceeds threshold -> escalates according to risk
    assert IncidentCorrelationEngine.determine_incident_severity("Low", "Low", 85.0) == "Critical"
    assert IncidentCorrelationEngine.determine_incident_severity("Low", "Low", 65.0) == "High"
    assert IncidentCorrelationEngine.determine_incident_severity("Low", "Low", 45.0) == "Medium"

    # 3. Monotonic Protection -> never downgrades
    assert IncidentCorrelationEngine.determine_incident_severity("Critical", "Low", 20.0) == "Critical"
    assert IncidentCorrelationEngine.determine_incident_severity("High", "Medium", 35.0) == "High"


def test_soc_phase1_feature_flag_toggle(monkeypatch):
    """Test disabling SOC_PHASE1_ENABLED falls back gracefully to pure ML prediction path."""
    from backend.app.config import settings
    monkeypatch.setattr(settings, "SOC_PHASE1_ENABLED", False)

    analyst_hdr = get_authenticated_headers("analyst")
    flow_payload = {
        "features": {
            "source_ip": "192.168.1.50",
            "destination_ip": "10.0.0.1",
            "destination_port": 80,
            "flow_duration": 1000.0,
            "packet_length_mean": 200.0
        },
        "model_name": "Random Forest"
    }
    res = client.post("/api/v1/predict/single", json=flow_payload, headers=analyst_hdr)
    assert res.status_code == 200
    assert "incident_id" in res.json()
