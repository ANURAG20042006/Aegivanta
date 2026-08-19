"""
tests/integration/test_phase3_real_pcap_e2e.py
==============================================
Phase 3.1 Real Network PCAP -> Flow -> Feature Extraction -> Live ML Model Integration Tests.
Verifies end-to-end telemetry ingestion, RBAC enforcement, live capture management,
and real ML inference without mocking.
"""

import io
import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from tests.unit.test_phase3_pcap_parsing import create_synthetic_pcap_bytes

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


def test_real_pcap_upload_to_live_ml_pipeline():
    """
    End-to-End Test:
    1. Authenticate as SOC analyst.
    2. Construct binary PCAP with multiple network flows.
    3. Upload to /api/v1/telemetry/pcap.
    4. Verify flow extraction and live ML classification across all models.
    """
    # 1. Login as Analyst
    headers = get_auth_headers("analyst")

    # 2. Build multi-packet binary PCAP
    # Flow A: 198.51.100.40 -> 10.0.0.5:80 (DDoS / High-volume SYN flood pattern)
    # Flow B: 192.168.1.55 -> 10.0.0.5:443 (Benign HTTPS session)
    packets_spec = [
        # Flow A Packets
        (100.00, "198.51.100.40", "10.0.0.5", 55501, 80, "TCP", b"X" * 500, {"syn": True}),
        (100.01, "198.51.100.40", "10.0.0.5", 55501, 80, "TCP", b"X" * 500, {"syn": True}),
        (100.02, "198.51.100.40", "10.0.0.5", 55501, 80, "TCP", b"X" * 500, {"syn": True}),
        (100.03, "198.51.100.40", "10.0.0.5", 55501, 80, "TCP", b"X" * 500, {"syn": True}),

        # Flow B Packets (Benign Web Traffic)
        (200.00, "192.168.1.55", "10.0.0.5", 60123, 443, "TCP", b"CLIENT_HELLO", {"syn": True}),
        (200.02, "10.0.0.5", "192.168.1.55", 443, 60123, "TCP", b"SERVER_HELLO", {"syn": True, "ack": True}),
        (200.04, "192.168.1.55", "10.0.0.5", 60123, 443, "TCP", b"TLS_APP_DATA", {"psh": True, "ack": True})
    ]
    pcap_bytes = create_synthetic_pcap_bytes(packets_spec)

    # 3. Post to /api/v1/telemetry/pcap with CatBoost model
    files = {"file": ("capture_test.pcap", io.BytesIO(pcap_bytes), "application/vnd.tcpdump.pcap")}
    res = client.post(
        "/api/v1/telemetry/pcap",
        files=files,
        data={"model_name": "CatBoost"},
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()

    # 4. Verify batch predictions
    assert data["total_packets_inspected"] == 2  # Exactly 2 bidirectional flows extracted
    assert len(data["results"]) == 2
    for r in data["results"]:
        assert r["model_used"] == "CatBoost"
        assert r["confidence_score"] is not None
        assert r["confidence_score"] >= 0.0 and r["confidence_score"] <= 1.0
        assert r["severity"] in ["Informational", "Low", "Medium", "High", "Critical"]
        assert r["protocol"] == "TCP"


def test_pcap_upload_rbac_and_validation():
    """Verify RBAC and input validation on PCAP upload endpoint."""
    # 1. Unauthenticated request rejected
    files = {"file": ("test.pcap", io.BytesIO(b"\x00" * 100), "application/octet-stream")}
    res = client.post("/api/v1/telemetry/pcap", files=files)
    assert res.status_code in [401, 403]

    # 2. Viewer role rejected (403 Forbidden)
    v_hdr = get_auth_headers("viewer")
    res_v = client.post(
        "/api/v1/telemetry/pcap",
        files={"file": ("test.pcap", io.BytesIO(b"\x00" * 100), "application/octet-stream")},
        headers=v_hdr
    )
    assert res_v.status_code == 403

    # 3. Invalid extension rejected (.txt instead of .pcap)
    a_hdr = get_auth_headers("analyst")
    res_ext = client.post(
        "/api/v1/telemetry/pcap",
        files={"file": ("malicious.exe", io.BytesIO(b"\x00" * 100), "application/octet-stream")},
        headers=a_hdr
    )
    assert res_ext.status_code == 400
    assert "Unsupported file format" in res_ext.json()["detail"]


def test_live_capture_control_and_prometheus_metrics():
    """Verify live capture lifecycle endpoints and Prometheus PCAP metrics."""
    admin_hdr = get_auth_headers("admin")

    # 1. Check live capture status
    status_res = client.get("/api/v1/telemetry/live/status", headers=admin_hdr)
    assert status_res.status_code == 200
    assert status_res.json()["status"] in ["IDLE", "CAPTURING", "STOPPED"]

    # 2. Start capture as Admin
    start_res = client.post("/api/v1/telemetry/live/start?interface=eth0", headers=admin_hdr)
    assert start_res.status_code == 200
    assert start_res.json()["session"]["status"] == "CAPTURING"

    # 3. Stop capture as Admin
    stop_res = client.post("/api/v1/telemetry/live/stop", headers=admin_hdr)
    assert stop_res.status_code == 200
    assert stop_res.json()["session"]["status"] == "STOPPED"

    # 4. Verify Prometheus metrics contains PCAP metrics
    prom_res = client.get("/api/v1/metrics/prometheus")
    assert prom_res.status_code == 200
    text = prom_res.text
    assert "sentinel_pcap_files_processed_total" in text
    assert "sentinel_pcap_packets_parsed_total" in text
    assert "sentinel_pcap_flows_extracted_total" in text
    assert "sentinel_pcap_parse_errors_total" in text
