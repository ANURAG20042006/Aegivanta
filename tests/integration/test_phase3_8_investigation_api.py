"""
tests/integration/test_phase3_8_investigation_api.py
====================================================
Phase 3.8 Integration Tests: Investigation Case Lifecycle REST APIs.
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def get_auth_headers(role: str = "analyst") -> dict:
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
def test_full_investigation_case_lifecycle():
    """Verify complete case lifecycle: create -> evidence -> note -> pivot -> timeline -> graph -> risk -> close."""
    headers = get_auth_headers("analyst")

    # 1. Create Case
    case_payload = {
        "title": "Operation Silent Shadow Investigation",
        "description": "Multi-stage intrusion targeting database crown jewel",
        "priority": "CRITICAL",
        "severity": "CRITICAL",
        "linked_incident_ids": ["inc-case-01"],
        "linked_assets": ["10.0.0.5"],
        "linked_users": ["db_admin"],
        "linked_iocs": ["198.51.100.99"],
        "mitre_techniques": ["T1078.001", "T1048"],
        "tags": ["apt", "database"]
    }
    res_c = client.post("/api/v1/investigations", json=case_payload, headers=headers)
    assert res_c.status_code == 201
    case_data = res_c.json()
    case_id = case_data["id"]

    # 2. Get Case Details
    res_get = client.get(f"/api/v1/investigations/{case_id}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["title"] == "Operation Silent Shadow Investigation"

    # 3. Add Evidence
    ev_payload = {
        "evidence_type": "FLOW_TELEMETRY",
        "reference_id": "flow-7788",
        "description": "Exfiltration flow observed transferring 8MB to 198.51.100.99",
        "metadata_json": {"bytes": 8000000}
    }
    res_ev = client.post(f"/api/v1/investigations/{case_id}/evidence", json=ev_payload, headers=headers)
    assert res_ev.status_code == 201

    # 4. Add Analyst Note
    res_note = client.post(f"/api/v1/investigations/{case_id}/notes", json={"content": "Confirmed data exfiltration pattern."}, headers=headers)
    assert res_note.status_code == 201

    # 5. Entity Pivot
    res_piv = client.post(f"/api/v1/investigations/{case_id}/pivot", json={"entity_type": "IP", "entity_value": "198.51.100.99"}, headers=headers)
    assert res_piv.status_code == 200

    # 6. Reconstructed Timeline
    res_tl = client.get(f"/api/v1/investigations/{case_id}/timeline", headers=headers)
    assert res_tl.status_code == 200
    assert len(res_tl.json()) >= 3  # Case created + Evidence + Note

    # 7. Correlated Evidence Graph
    res_g = client.get(f"/api/v1/investigations/{case_id}/graph", headers=headers)
    assert res_g.status_code == 200
    assert "nodes" in res_g.json()
    assert "edges" in res_g.json()

    # 8. Risk Breakdown
    res_risk = client.get(f"/api/v1/investigations/{case_id}/risk", headers=headers)
    assert res_risk.status_code == 200
    assert "total_risk_score" in res_risk.json()

    # 9. MITRE Coverage
    res_mitre = client.get(f"/api/v1/investigations/{case_id}/mitre", headers=headers)
    assert res_mitre.status_code == 200

    # 10. Close Case
    res_close = client.post(f"/api/v1/investigations/{case_id}/close", json={"resolution_summary": "Attacker IP blocked, credentials rotated."}, headers=headers)
    assert res_close.status_code == 200
    assert res_close.json()["current_status"] == "CLOSED"

    # 11. Verify Statistics
    res_stats = client.get("/api/v1/investigations/statistics", headers=headers)
    assert res_stats.status_code == 200
    assert res_stats.json()["total_cases"] >= 1
