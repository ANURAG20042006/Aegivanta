"""
tests/integration/test_phase39_simulation_flow.py
=================================================
Phase 39 Adversarial Simulation & Horizon Trends Flow Integration Tests.
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
    """Integration tests for listing adversarial simulations and global horizon indicators."""

    def test_simulations_and_horizon_indicators(self, client, auth_headers):
        """Test listing simulations and horizon indicators."""
        # 1. List Simulations
        sims_resp = client.get("/api/v1/predictive-intel/simulations", headers=auth_headers)
        assert sims_resp.status_code == 200
        sims = sims_resp.json()
        assert len(sims) >= 1
        assert "estimated_blast_radius_nodes" in sims[0]

        # 2. List Horizon Indicators
        inds_resp = client.get("/api/v1/predictive-intel/horizon-indicators", headers=auth_headers)
        assert inds_resp.status_code == 200
        inds = inds_resp.json()
        assert len(inds) >= 1
        assert "observed_global_sightings" in inds[0]
