"""
tests/integration/test_phase3_6_incident_api.py
===============================================
Phase 3.6 Integration Tests: Incident REST API & Investigation Lifecycle Endpoints.
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

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


@pytest.mark.integration
def test_api_incident_correlate_and_lifecycle_flow():
    """Verify full end-to-end incident lifecycle from correlation to resolution."""
    headers = get_auth_headers("admin")

    # 1. Trigger correlation batch
    payload = {
        "events": [
            {
                "id": "batch-ev-1",
                "source_ip": "198.51.100.50",
                "destination_ip": "10.0.0.15",
                "destination_port": 445,
                "protocol": "TCP",
                "is_malicious": True,
                "attack_type": "Brute Force",
                "auth_failures": 6,
                "timestamp": "2026-08-20T10:00:00Z"
            }
        ],
        "window_minutes": 15
    }
    res_corr = client.post("/api/v1/incidents/correlate", json=payload, headers=headers)
    assert res_corr.status_code == 200
    corr_data = res_corr.json()
    assert corr_data["total_events_processed"] == 1
    assert corr_data["total_correlated_bundles"] >= 1
    inc_id = corr_data["incidents"][0]["incident_id"]

    # 2. Get incident details
    res_detail = client.get(f"/api/v1/incidents/{inc_id}", headers=headers)
    assert res_detail.status_code == 200
    detail_data = res_detail.json()
    assert detail_data["id"] == inc_id
    assert detail_data["status"] in ["OPEN", "DETECTED"]

    # 3. Get timeline
    res_tl = client.get(f"/api/v1/incidents/{inc_id}/timeline", headers=headers)
    assert res_tl.status_code == 200
    tl_data = res_tl.json()
    assert "summary" in tl_data
    assert len(tl_data["timeline"]) >= 1

    # 4. Get risk breakdown
    res_risk = client.get(f"/api/v1/incidents/{inc_id}/risk", headers=headers)
    assert res_risk.status_code == 200
    risk_data = res_risk.json()
    assert "components" in risk_data

    # 5. Get evidence
    res_ev = client.get(f"/api/v1/incidents/{inc_id}/evidence", headers=headers)
    assert res_ev.status_code == 200
    ev_data = res_ev.json()
    assert ev_data["source_ip"] == "198.51.100.50"

    # 6. Assign incident
    res_assign = client.post(
        f"/api/v1/incidents/{inc_id}/assign",
        json={"analyst_username": "analyst"},
        headers=headers
    )
    assert res_assign.status_code == 200
    assert res_assign.json()["assigned_analyst"] == "analyst"

    # 7. Transition status to INVESTIGATING
    res_status = client.post(
        f"/api/v1/incidents/{inc_id}/status",
        json={"status": "INVESTIGATING", "notes": "Beginning forensic packet analysis"},
        headers=headers
    )
    assert res_status.status_code == 200
    assert res_status.json()["current_status"] == "INVESTIGATING"

    # 8. Resolve incident
    res_res = client.post(
        f"/api/v1/incidents/{inc_id}/resolve",
        json={"resolution_notes": "Host isolated and credentials revoked.", "remediation_action": "ISOLATE_HOST"},
        headers=headers
    )
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "RESOLVED"


@pytest.mark.integration
def test_api_mitre_coverage_and_statistics_endpoints():
    """Verify GET /api/v1/incidents/mitre-coverage and /statistics endpoints."""
    headers = get_auth_headers("viewer")

    # MITRE Coverage
    res_mitre = client.get("/api/v1/incidents/mitre-coverage", headers=headers)
    assert res_mitre.status_code == 200
    mitre_data = res_mitre.json()
    assert mitre_data["total_catalog_techniques"] > 15
    assert mitre_data["covered_techniques_count"] >= 10
    assert mitre_data["coverage_percentage"] > 0

    # Statistics
    res_stats = client.get("/api/v1/incidents/statistics", headers=headers)
    assert res_stats.status_code == 200
    stats_data = res_stats.json()
    assert "total_incidents" in stats_data
    assert "by_status" in stats_data
    assert "by_severity" in stats_data
