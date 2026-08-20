"""
tests/security/test_phase3_6_incident_rbac.py
=============================================
Phase 3.6 Security & RBAC Boundary Tests: Incident REST Endpoints.
Verifies role authorization boundaries (admin, analyst, viewer, unauthenticated).
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def get_auth_headers(role: str) -> dict:
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


@pytest.mark.security
def test_unauthenticated_request_rejected():
    """Verify unauthenticated requests return 401 Unauthorized."""
    res = client.get("/api/v1/incidents/statistics")
    assert res.status_code == 401


@pytest.mark.security
def test_viewer_cannot_assign_or_resolve_incident():
    """Verify viewer role is blocked from modifying incident state (403 Forbidden)."""
    headers = get_auth_headers("viewer")

    # Viewer cannot assign
    res_assign = client.post("/api/v1/incidents/inc-test-01/assign", json={"analyst_username": "viewer"}, headers=headers)
    assert res_assign.status_code == 403

    # Viewer cannot resolve
    res_res = client.post("/api/v1/incidents/inc-test-01/resolve", json={"resolution_notes": "test"}, headers=headers)
    assert res_res.status_code == 403

    # Viewer cannot transition status
    res_stat = client.post("/api/v1/incidents/inc-test-01/status", json={"status": "RESOLVED"}, headers=headers)
    assert res_stat.status_code == 403


@pytest.mark.security
def test_analyst_can_access_investigation_endpoints():
    """Verify analyst role has full operational access to investigate and view incidents."""
    headers = get_auth_headers("analyst")

    res_stats = client.get("/api/v1/incidents/statistics", headers=headers)
    assert res_stats.status_code == 200

    res_mitre = client.get("/api/v1/incidents/mitre-coverage", headers=headers)
    assert res_mitre.status_code == 200
