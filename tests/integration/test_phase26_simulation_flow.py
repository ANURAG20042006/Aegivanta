"""
tests/integration/test_phase26_simulation_flow.py
=================================================
Phase 26 Defensive Attack Simulation Integration Flow Tests.
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    password = os.getenv("SENTINEL_ADMIN_PASSWORD", "TestAdminPassword2026!")
    res = client.post("/api/v1/auth/login", data={"username": "admin", "password": password})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestSimulationFlow:
    """Integration flow for defensive attack simulations and purple-team reports."""

    def test_simulation_catalog_and_trigger_flow(self, client, auth_headers):
        """GET /api/v1/security/simulations/catalog and POST /api/v1/security/simulations."""
        cat_resp = client.get("/api/v1/security/simulations/catalog", headers=auth_headers)
        assert cat_resp.status_code == 200
        catalog = cat_resp.json()
        assert len(catalog) == 10

        # Trigger simulation
        trigger_resp = client.post(
            "/api/v1/security/simulations",
            json={"attack_technique": "T1110_BRUTE_FORCE"},
            headers=auth_headers
        )
        assert trigger_resp.status_code == 200
        sim_data = trigger_resp.json()
        sim_id = sim_data["id"]
        assert sim_data["coverage_result"] == "FULL"
        assert sim_data["status"] == "COMPLETED"

        # Fetch details
        det_resp = client.get(f"/api/v1/security/simulations/{sim_id}", headers=auth_headers)
        assert det_resp.status_code == 200
        assert len(det_resp.json()["events"]) > 0

        # Fetch Purple Team Report
        rep_resp = client.get(f"/api/v1/security/simulations/{sim_id}/report", headers=auth_headers)
        assert rep_resp.status_code == 200
        rep_data = rep_resp.json()
        assert rep_data["verdict"] == "PASSED"
        assert rep_data["metrics"]["detection_rate_pct"] == 100.0
