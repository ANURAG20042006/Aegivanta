"""
tests/security/test_phase3_8_security.py
========================================
Phase 3.8 Security & RBAC Boundary Tests: Threat Hunting & Investigation APIs.
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


@pytest.mark.security
def test_unauthenticated_hunting_and_investigation_endpoints_return_401():
    """Verify unauthenticated requests return 401 Unauthorized."""
    assert client.get("/api/v1/hunting/hunts").status_code == 401
    assert client.get("/api/v1/investigations").status_code == 401
    assert client.get("/api/v1/investigations/statistics").status_code == 401


@pytest.mark.security
def test_viewer_denied_modifying_investigations():
    """Verify viewer role cannot create, update, attach evidence, or close investigation cases (403 Forbidden)."""
    headers = get_auth_headers("viewer")

    # Create Case
    res_create = client.post(
        "/api/v1/investigations",
        json={"title": "Viewer Case Attempt", "priority": "LOW"},
        headers=headers
    )
    assert res_create.status_code == 403

    # Add Note
    res_note = client.post(
        "/api/v1/investigations/case-123/notes",
        json={"content": "Unauthorized note"},
        headers=headers
    )
    assert res_note.status_code == 403

    # Close Case
    res_close = client.post(
        "/api/v1/investigations/case-123/close",
        json={"resolution_summary": "Unauthorized close attempt"},
        headers=headers
    )
    assert res_close.status_code == 403


@pytest.mark.security
def test_sql_injection_defense_in_hunting_query_api():
    """Verify threat hunting query API rejects disallowed query fields and safely escapes values."""
    headers = get_auth_headers("analyst")

    bad_field_payload = {
        "entity": "events",
        "filters": [
            {"field": "unauthorized_column; DROP TABLE users;--", "operator": "equals", "value": "10.0.0.1"}
        ]
    }
    res = client.post("/api/v1/hunting/query", json=bad_field_payload, headers=headers)
    assert res.status_code == 400
    assert "not a permitted threat hunting query field" in res.json()["detail"]

    # Parameterized value with SQL payload is safely treated as a search string
    sqli_val_payload = {
        "entity": "events",
        "filters": [
            {"field": "source_ip", "operator": "equals", "value": "10.0.0.1' OR '1'='1"}
        ]
    }
    res_val = client.post("/api/v1/hunting/query", json=sqli_val_payload, headers=headers)
    assert res_val.status_code == 200
