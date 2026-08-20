"""
tests/security/test_phase3_7_response_rbac.py
=============================================
Phase 3.7 Security & RBAC Boundary Tests: SOAR Response APIs.
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
def test_unauthenticated_response_endpoint_rejected():
    """Verify unauthenticated requests to response APIs return 401 Unauthorized."""
    res = client.get("/api/v1/response/policies")
    assert res.status_code == 401

    res_stat = client.get("/api/v1/response/statistics")
    assert res_stat.status_code == 401


@pytest.mark.security
def test_viewer_cannot_submit_or_approve_remediation():
    """Verify viewer role is blocked from requesting, approving, or modifying response policies (403 Forbidden)."""
    headers = get_auth_headers("viewer")

    # Viewer cannot submit action
    res_sub = client.post(
        "/api/v1/response/actions",
        json={"incident_id": "test-inc", "action_type": "BLOCK_IP", "target_entity": "1.2.3.4"},
        headers=headers
    )
    assert res_sub.status_code == 403

    # Viewer cannot approve action
    res_app = client.post("/api/v1/response/actions/act-123/approve", headers=headers)
    assert res_app.status_code == 403

    # Viewer cannot create policies
    res_pol = client.post(
        "/api/v1/response/policies",
        json={"name": "VIEWER_POLICY", "minimum_risk_score": 10.0},
        headers=headers
    )
    assert res_pol.status_code == 403


@pytest.mark.security
def test_analyst_can_evaluate_and_preview_actions():
    """Verify analyst role has permissions to evaluate, preview, and query SOAR statistics."""
    headers = get_auth_headers("analyst")

    # Evaluate
    res_eval = client.post(
        "/api/v1/response/evaluate",
        json={"incident_id": "test-inc-01", "risk_score": 65.0, "severity": "HIGH"},
        headers=headers
    )
    assert res_eval.status_code == 200
    assert "decision" in res_eval.json()

    # Preview
    res_prev = client.post(
        "/api/v1/response/actions/preview",
        json={"incident_id": "test-inc-01", "action_type": "BLOCK_IP", "target_entity": "198.51.100.9"},
        headers=headers
    )
    assert res_prev.status_code == 200
    assert res_prev.json()["would_execute"] is True
