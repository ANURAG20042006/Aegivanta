"""
tests/integration/test_phase3_8_hunting_api.py
==============================================
Phase 3.8 Integration Tests: Threat Hunting REST APIs.
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
def test_hunting_api_query_list_and_run():
    """Verify threat hunting APIs: query DSL, list hunts, get hunt details, run hunt."""
    headers = get_auth_headers("analyst")

    # 1. Execute Query DSL
    query_payload = {
        "entity": "events",
        "filters": [{"field": "protocol", "operator": "equals", "value": "TCP"}],
        "limit": 50
    }
    res_q = client.post("/api/v1/hunting/query", json=query_payload, headers=headers)
    assert res_q.status_code == 200
    assert "results" in res_q.json()

    # 2. List Modular Hunts
    res_hunts = client.get("/api/v1/hunting/hunts", headers=headers)
    assert res_hunts.status_code == 200
    hunts = res_hunts.json()
    assert len(hunts) == 10
    assert any(h["hunt_id"] == "HUNT-001" for h in hunts)

    # 3. Get Hunt Details
    res_det = client.get("/api/v1/hunting/hunts/HUNT-001", headers=headers)
    assert res_det.status_code == 200
    assert res_det.json()["hunt_id"] == "HUNT-001"

    # 4. Run Hunt Rule
    run_payload = {
        "events": [
            {"username": "test_victim", "auth_failures": 5, "auth_success": True}
        ]
    }
    res_run = client.post("/api/v1/hunting/run/HUNT-001", json=run_payload, headers=headers)
    assert res_run.status_code == 200
    assert res_run.json()["total_findings"] >= 1
