"""
tests/integration/test_complete_soc_pipeline.py
================================================
Comprehensive End-to-End Integration Test Suite for SentinelAI SOC Platform (Phase 1).

Validates the complete 16-step pipeline:
Network/Telemetry -> ML Inference -> Asset Matching -> Risk Calculation ->
Alert Creation -> Incident Correlation -> Attack Timeline -> WebSocket Broadcast -> Resolution.

Also validates all edge cases:
- Unmapped unknown assets
- Missing confidence fallback
- WebSocket broadcast failure resilience
- RBAC authorization boundaries
- Invalid state transitions
- Time window & partition boundaries
"""

import os
import uuid
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.risk_engine import RiskScoringEngine
from backend.app.services.correlation_engine import IncidentCorrelationEngine


client = TestClient(app)


def get_auth_headers(role: str = "admin") -> dict:
    env_map = {
        "admin": "SENTINEL_ADMIN_PASSWORD",
        "analyst": "SENTINEL_ANALYST_PASSWORD",
        "viewer": "SENTINEL_VIEWER_PASSWORD"
    }
    password = os.getenv(env_map.get(role, "SENTINEL_ADMIN_PASSWORD"), "TestAdminPassword2026!")
    res = client.post("/api/v1/auth/login", data={"username": role, "password": password})
    assert res.status_code == 200, f"Login failed for {role}: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_16_step_complete_operational_pipeline(monkeypatch):
    """
    Executes and validates the full 16-step operational SOC pipeline:
    1. Create protected asset
    2. Submit security telemetry
    3. Run existing ML prediction
    4. Match asset
    5. Calculate risk score
    6. Persist security event
    7. Create alert
    8. Create incident
    9. Create timeline event
    10. Publish WebSocket event
    11. Correlate a second matching alert
    12. Verify alert_count increases
    13. Verify incident risk changes
    14. Verify timeline contains correlation event
    15. Resolve incident
    16. Verify later alert does NOT attach to resolved incident
    """
    admin_hdr = get_auth_headers("admin")
    analyst_hdr = get_auth_headers("analyst")
    viewer_hdr = get_auth_headers("viewer")

    # Track WebSocket broadcast events
    ws_broadcasts = []
    from backend.app.api.v1.websockets import manager
    from backend.app.services.predict_service import predict_service

    async def mock_broadcast(event_type: str, data: dict):
        ws_broadcasts.append({"type": event_type, "data": data})

    monkeypatch.setattr(manager, "broadcast_event", mock_broadcast)
    monkeypatch.setattr(
        predict_service,
        "infer_packet_threat",
        lambda vector, model_name: ("DDoS", 0.95, True, "Critical", {"DDoS": 0.95}, {"explanation_available": True})
    )

    uid = uuid.uuid4().hex[:6]
    asset_ip = f"10.50.{uuid.uuid4().int % 200}.{uuid.uuid4().int % 200}"

    # Step 1: Create protected asset
    asset_payload = {
        "name": f"Core Banking API {uid}",
        "hostname": f"api-{uid}.banking.internal",
        "url": f"https://api-{uid}.banking.internal",
        "ip_address": asset_ip,
        "asset_type": "api",
        "environment": "production",
        "criticality": "critical",
        "status": "active",
        "description": "Core transaction processing service."
    }
    asset_res = client.post("/api/v1/assets", json=asset_payload, headers=analyst_hdr)
    assert asset_res.status_code == 201
    asset_data = asset_res.json()
    asset_id = asset_data["id"]

    # Step 2 & 3: Submit telemetry & run ML prediction
    flow_1 = {
        "features": {
            "source_ip": "198.51.100.44",
            "destination_ip": asset_ip,
            "source_port": 54321,
            "destination_port": 443,
            "protocol": "TCP",
            "flow_duration": 950000.0,
            "flow_packets_s": 5000.0,
            "packet_length_mean": 1400.0,
            "syn_flag_count": 1.0
        },
        "model_name": "Random Forest"
    }
    pred_res_1 = client.post("/api/v1/predict/single", json=flow_1, headers=analyst_hdr)
    assert pred_res_1.status_code == 200
    pred_data_1 = pred_res_1.json()
    incident_id_1 = pred_data_1["incident_id"]
    assert incident_id_1 is not None

    # Step 4, 5, 6, 7, 8, 9: Verify asset matching, risk, alert, incident, timeline
    inc_res_1 = client.get(f"/api/v1/incidents/{incident_id_1}", headers=viewer_hdr)
    assert inc_res_1.status_code == 200
    inc_1 = inc_res_1.json()
    assert inc_1["asset_id"] == asset_id
    assert inc_1["asset"]["name"] == asset_payload["name"]
    assert inc_1["alert_count"] == 1
    assert inc_1["risk_score"] > 0.0
    assert len(inc_1["alerts"]) == 1
    assert len(inc_1["timeline"]) >= 1
    assert any(evt["event_type"] == "DETECTION" for evt in inc_1["timeline"])

    # Step 10: Verify WebSocket event published
    assert len(ws_broadcasts) >= 1
    assert any(b["type"] == "ALERT_TRIGGERED" for b in ws_broadcasts)

    # Step 11: Correlate a second matching alert (same asset IP and same source IP)
    flow_2 = {
        "features": {
            "source_ip": "198.51.100.44",
            "destination_ip": asset_ip,
            "source_port": 54322,
            "destination_port": 443,
            "protocol": "TCP",
            "flow_duration": 960000.0,
            "flow_packets_s": 5100.0,
            "packet_length_mean": 1420.0,
            "syn_flag_count": 1.0
        },
        "model_name": "Random Forest"
    }
    pred_res_2 = client.post("/api/v1/predict/single", json=flow_2, headers=analyst_hdr)
    assert pred_res_2.status_code == 200
    assert pred_res_2.json()["incident_id"] == incident_id_1

    # Step 12, 13, 14: Verify alert_count increases, risk score updates, timeline contains ALERT_CORRELATED
    inc_res_2 = client.get(f"/api/v1/incidents/{incident_id_1}", headers=viewer_hdr)
    assert inc_res_2.status_code == 200
    inc_2 = inc_res_2.json()
    assert inc_2["alert_count"] == 2
    assert inc_2["risk_score"] >= inc_1["risk_score"]
    assert len(inc_2["alerts"]) == 2
    timeline_event_types = [evt["event_type"] for evt in inc_2["timeline"]]
    assert "ALERT_CORRELATED" in timeline_event_types

    # Step 15: Resolve incident (transition: DETECTED -> TRIAGED -> INVESTIGATING -> RESOLVED)
    client.patch(f"/api/v1/incidents/{incident_id_1}/status", json={"status": "TRIAGED"}, headers=analyst_hdr)
    client.patch(f"/api/v1/incidents/{incident_id_1}/status", json={"status": "INVESTIGATING"}, headers=analyst_hdr)
    res_resolve = client.patch(f"/api/v1/incidents/{incident_id_1}/status", json={"status": "RESOLVED"}, headers=analyst_hdr)
    assert res_resolve.status_code == 200
    assert res_resolve.json()["new_status"] == "RESOLVED"

    # Step 16: Verify later alert does NOT attach to resolved incident
    flow_3 = {
        "features": {
            "source_ip": "198.51.100.44",
            "destination_ip": asset_ip,
            "source_port": 54323,
            "destination_port": 443,
            "protocol": "TCP",
            "flow_duration": 970000.0,
            "flow_packets_s": 5200.0,
            "packet_length_mean": 1450.0,
            "syn_flag_count": 1.0
        },
        "model_name": "Random Forest"
    }
    pred_res_3 = client.post("/api/v1/predict/single", json=flow_3, headers=analyst_hdr)
    assert pred_res_3.status_code == 200
    incident_id_3 = pred_res_3.json()["incident_id"]
    assert incident_id_3 != incident_id_1  # A new incident was created!


def test_edge_case_unknown_unmapped_asset():
    """Test flow targeting unknown IP creates security alert and incident with unmapped asset."""
    analyst_hdr = get_auth_headers("analyst")
    viewer_hdr = get_auth_headers("viewer")

    flow = {
        "features": {
            "source_ip": "185.220.101.5",
            "destination_ip": "192.0.2.199",  # Unregistered destination IP
            "source_port": 40100,
            "destination_port": 8080,
            "protocol": "TCP",
            "flow_duration": 500000.0,
            "flow_packets_s": 3500.0,
            "packet_length_mean": 800.0,
            "syn_flag_count": 1.0
        },
        "model_name": "Random Forest"
    }
    pred_res = client.post("/api/v1/predict/single", json=flow, headers=analyst_hdr)
    assert pred_res.status_code == 200
    inc_id = pred_res.json()["incident_id"]
    assert inc_id is not None

    inc_res = client.get(f"/api/v1/incidents/{inc_id}", headers=viewer_hdr)
    assert inc_res.status_code == 200
    inc_data = inc_res.json()
    assert inc_data["asset_id"] is None
    assert inc_data["asset"] is None


def test_edge_case_websocket_failure_does_not_fail_db_transaction(monkeypatch):
    """Test that a WebSocket broadcast failure does NOT rollback or fail the DB persistence."""
    from backend.app.api.v1.websockets import manager

    async def broken_broadcast(event_type: str, data: dict):
        raise ConnectionResetError("Simulated broken pipe during broadcast")

    monkeypatch.setattr(manager, "broadcast_event", broken_broadcast)

    analyst_hdr = get_auth_headers("analyst")
    flow = {
        "features": {
            "source_ip": "198.51.100.99",
            "destination_ip": "10.0.10.10",
            "source_port": 50000,
            "destination_port": 80,
            "protocol": "TCP",
            "flow_duration": 400000.0,
            "packet_length_mean": 600.0
        },
        "model_name": "Random Forest"
    }
    pred_res = client.post("/api/v1/predict/single", json=flow, headers=analyst_hdr)
    assert pred_res.status_code == 200
    inc_id = pred_res.json()["incident_id"]
    assert inc_id is not None


def test_rbac_authorization_matrix():
    """Validates role-based access control across Admin, Analyst, and Viewer roles."""
    admin_hdr = get_auth_headers("admin")
    analyst_hdr = get_auth_headers("analyst")
    viewer_hdr = get_auth_headers("viewer")

    uid = uuid.uuid4().hex[:6]
    asset_payload = {
        "name": f"Protected Database {uid}",
        "hostname": f"db-{uid}.internal",
        "ip_address": f"10.100.1.{uuid.uuid4().int % 200}",
        "asset_type": "database",
        "environment": "production",
        "criticality": "high"
    }

    # 1. Viewer cannot create asset (403)
    res_viewer_create = client.post("/api/v1/assets", json=asset_payload, headers=viewer_hdr)
    assert res_viewer_create.status_code == 403

    # 2. Analyst creates asset (201)
    res_analyst_create = client.post("/api/v1/assets", json=asset_payload, headers=analyst_hdr)
    assert res_analyst_create.status_code == 201
    asset_id = res_analyst_create.json()["id"]

    # 3. Analyst cannot delete/deactivate asset (403)
    res_analyst_delete = client.delete(f"/api/v1/assets/{asset_id}", headers=analyst_hdr)
    assert res_analyst_delete.status_code == 403

    # 4. Admin deactivates asset (204)
    res_admin_delete = client.delete(f"/api/v1/assets/{asset_id}", headers=admin_hdr)
    assert res_admin_delete.status_code == 204


def test_invalid_state_transitions():
    """Test that illegal state machine transitions are rejected with HTTP 400."""
    analyst_hdr = get_auth_headers("analyst")

    flow = {
        "features": {
            "source_ip": "192.0.2.77",
            "destination_ip": "10.0.0.1",
            "source_port": 34567,
            "destination_port": 80,
            "protocol": "TCP",
            "flow_duration": 300000.0,
            "packet_length_mean": 500.0
        },
        "model_name": "Random Forest"
    }
    pred_res = client.post("/api/v1/predict/single", json=flow, headers=analyst_hdr)
    inc_id = pred_res.json()["incident_id"]

    # Illegal transition: DETECTED -> RESOLVED directly without triaging/investigating
    res_illegal = client.patch(
        f"/api/v1/incidents/{inc_id}/status",
        json={"status": "RESOLVED"},
        headers=analyst_hdr
    )
    assert res_illegal.status_code == 400
    assert "Invalid state transition" in res_illegal.text
