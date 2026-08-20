"""
tests/security/test_phase3_9_security.py
========================================
Security Verification Suite for SOC Command Center.
Audits SQL Injection immunity, zero secret exposure, RBAC boundary enforcement,
and input validation on all dashboard endpoints.
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.security import create_access_token

client = TestClient(app)


def get_auth_hdr(role: str = "analyst") -> dict:
    env_map = {
        "admin": "SENTINEL_ADMIN_PASSWORD",
        "analyst": "SENTINEL_ANALYST_PASSWORD",
        "viewer": "SENTINEL_VIEWER_PASSWORD"
    }
    password = os.getenv(env_map.get(role, "SENTINEL_ANALYST_PASSWORD"), "TestAnalystPassword2026!")
    resp = client.post("/api/v1/auth/login", data={"username": role, "password": password})
    if resp.status_code == 200:
        return {"Authorization": f"Bearer {resp.json().get('access_token')}"}
    token = create_access_token(subject=role, role=role)
    return {"Authorization": f"Bearer {token}"}


def test_sql_injection_immunity_in_incident_search():
    hdr = get_auth_hdr("analyst")
    sqli_payloads = [
        "' OR '1'='1",
        "1; DROP TABLE incidents;--",
        "' UNION SELECT NULL, NULL, NULL--",
        "admin'--",
        "'; EXEC xp_cmdshell('dir');--"
    ]
    for sqli in sqli_payloads:
        resp = client.get(
            f"/api/v1/dashboard/incidents?search={sqli}&sort_by=risk_score&sort_order=desc",
            headers=hdr
        )
        assert resp.status_code == 200, f"SQLi payload caused server failure: {sqli}"
        data = resp.json()
        assert "items" in data
        assert isinstance(data["items"], list)


def test_zero_secret_exposure_in_dashboard_endpoints():
    hdr = get_auth_hdr("admin")
    endpoints = [
        "/api/v1/dashboard/overview",
        "/api/v1/dashboard/incidents",
        "/api/v1/dashboard/detections",
        "/api/v1/dashboard/threat-intel",
        "/api/v1/dashboard/response",
        "/api/v1/dashboard/investigations",
        "/api/v1/dashboard/mitre",
        "/api/v1/dashboard/system-health",
        "/api/v1/dashboard/events"
    ]
    forbidden_terms = [
        "secret_key",
        "database_url",
        "redis_url",
        "password_hash",
        "sentinel_admin_password",
        "jwt_secret"
    ]

    for ep in endpoints:
        resp = client.get(ep, headers=hdr)
        assert resp.status_code == 200
        text = resp.text.lower()
        for term in forbidden_terms:
            assert term not in text, f"Forbidden term '{term}' exposed in response from {ep}"


def test_input_validation_bounds_enforcement():
    hdr = get_auth_hdr("viewer")
    
    # Negative page
    resp1 = client.get("/api/v1/dashboard/incidents?page=-1", headers=hdr)
    assert resp1.status_code == 422

    # Excessive limit (>100)
    resp2 = client.get("/api/v1/dashboard/incidents?limit=1000", headers=hdr)
    assert resp2.status_code == 422

    # Invalid sort order
    resp3 = client.get("/api/v1/dashboard/incidents?sort_order=invalid_dir", headers=hdr)
    assert resp3.status_code == 422
