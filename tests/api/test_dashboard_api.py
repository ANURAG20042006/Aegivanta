"""
tests/api/test_dashboard_api.py
===============================
Integration and RBAC tests for SOC Command Center Dashboard REST API endpoints (/api/v1/dashboard/*).
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def get_headers(username: str = "admin") -> dict:
    env_map = {
        "admin": "SENTINEL_ADMIN_PASSWORD",
        "analyst": "SENTINEL_ANALYST_PASSWORD",
        "viewer": "SENTINEL_VIEWER_PASSWORD"
    }
    password = os.getenv(env_map.get(username, "SENTINEL_ADMIN_PASSWORD"), "TestAdminPassword2026!")
    resp = client.post("/api/v1/auth/login", data={"username": username, "password": password})
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    return {}


def test_dashboard_unauthenticated_requests_fail():
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
    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code in [401, 403], f"Expected 401/403 for {ep}, got {resp.status_code}"


def test_dashboard_overview_endpoint():
    hdr = get_headers("analyst")
    resp = client.get("/api/v1/dashboard/overview", headers=hdr)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_incidents" in data
    assert "open_incidents" in data
    assert "mean_time_to_detect_minutes" in data
    assert "mean_time_to_acknowledge_minutes" in data
    assert "mean_time_to_respond_minutes" in data
    assert "mean_time_to_resolve_minutes" in data
    assert "active_investigations" in data
    assert "active_soar_actions" in data
    assert "mitre_coverage_pct" in data


def test_dashboard_incidents_endpoint():
    hdr = get_headers("viewer")
    resp = client.get("/api/v1/dashboard/incidents?page=1&limit=10", headers=hdr)
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "page" in data
    assert "limit" in data
    assert "items" in data
    assert isinstance(data["items"], list)


def test_dashboard_detections_endpoint():
    hdr = get_headers("analyst")
    resp = client.get("/api/v1/dashboard/detections", headers=hdr)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_detections" in data
    assert "attack_type_distribution" in data
    assert "severity_breakdown" in data


def test_dashboard_threat_intel_endpoint():
    hdr = get_headers("admin")
    resp = client.get("/api/v1/dashboard/threat-intel", headers=hdr)
    assert resp.status_code == 200
    data = resp.json()
    assert "active_indicators_count" in data
    assert "total_feeds" in data
    assert "cache_stats" in data


def test_dashboard_response_endpoint():
    hdr = get_headers("analyst")
    resp = client.get("/api/v1/dashboard/response", headers=hdr)
    assert resp.status_code == 200
    data = resp.json()
    assert "pending_approvals_count" in data
    assert "executing_actions_count" in data
    assert "average_response_latency_ms" in data


def test_dashboard_investigations_endpoint():
    hdr = get_headers("analyst")
    resp = client.get("/api/v1/dashboard/investigations", headers=hdr)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_investigations" in data
    assert "status_breakdown" in data


def test_dashboard_mitre_endpoint():
    hdr = get_headers("viewer")
    resp = client.get("/api/v1/dashboard/mitre", headers=hdr)
    assert resp.status_code == 200
    data = resp.json()
    assert "coverage_percentage" in data
    assert "covered_techniques" in data


def test_dashboard_system_health_endpoint():
    hdr = get_headers("admin")
    resp = client.get("/api/v1/dashboard/system-health", headers=hdr)
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_status" in data
    assert "components" in data
    assert "postgresql" in data["components"]
    assert "redis" in data["components"]
    # Verify no secret or password in body
    body_str = resp.text.lower()
    assert "password" not in body_str
    assert "secret_key" not in body_str


def test_dashboard_events_endpoint():
    hdr = get_headers("analyst")
    resp = client.get("/api/v1/dashboard/events?limit=20", headers=hdr)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
