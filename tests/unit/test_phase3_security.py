"""
tests/unit/test_phase3_security.py
==================================
Unit tests for Phase 3 RBAC, Rate Limiting, and Injection Protection.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings

client = TestClient(app)


def get_auth_token(role: str = "admin") -> dict:
    passwords = {
        "admin": [getattr(settings, "SENTINEL_ADMIN_PASSWORD", "Admin_Secure2026!"), "TestAdminPassword2026!"],
        "analyst": [getattr(settings, "SENTINEL_ANALYST_PASSWORD", "Analyst_Secure2026!"), "TestAnalystPassword2026!"],
        "viewer": [getattr(settings, "SENTINEL_VIEWER_PASSWORD", "Viewer_Secure2026!"), "TestViewerPassword2026!"]
    }
    candidates = passwords.get(role, ["Admin_Secure2026!"])
    token = None
    for pwd in candidates:
        resp = client.post("/api/v1/auth/login", data={"username": role, "password": pwd})
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            break
    assert token is not None, f"Authentication failed for {role}"
    return {"Authorization": f"Bearer {token}"}


def test_viewer_denied_saving_hunting_query():
    """Verify Viewer cannot save query templates."""
    viewer_hdr = get_auth_token("viewer")
    res = client.post("/api/v1/hunting/saved", json={
        "name": "Unauthorized Query",
        "query_definition": {}
    }, headers=viewer_hdr)
    assert res.status_code == 403


def test_analyst_denied_approving_response_action():
    """Verify Analyst cannot approve response actions (Admin only)."""
    analyst_hdr = get_auth_token("analyst")
    res = client.post("/api/v1/response/approve/sample-id", headers=analyst_hdr)
    assert res.status_code == 403


def test_hunting_query_sql_injection_defense():
    """Verify SQL injection payloads in hunting queries are safely escaped through ORM parameters."""
    analyst_hdr = get_auth_token("analyst")
    sqli_payload = {
        "entity": "alerts",
        "filters": {
            "source_ip": "127.0.0.1' OR '1'='1",
            "attack_type": "'; DROP TABLE alerts; --"
        },
        "limit": 10
    }
    res = client.post("/api/v1/hunting/query", json=sqli_payload, headers=analyst_hdr)
    assert res.status_code == 200
    data = res.json()
    assert data["result_count"] == 0
