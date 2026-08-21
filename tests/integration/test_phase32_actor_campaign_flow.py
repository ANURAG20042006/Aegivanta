"""
tests/integration/test_phase32_actor_campaign_flow.py
=====================================================
Phase 32 Threat Actor Profiles & Campaign Heatmap Integration Tests.
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


class TestActorCampaignIntegrationFlow:
    """Integration tests for Threat Actor profiles, ATT&CK heatmaps, and hunting query generation."""

    def test_actors_heatmaps_and_hunting_dispatcher_flow(self, client, auth_headers):
        """Test threat actors list, campaign heatmaps, and automated query generation."""
        # 1. Threat Actors
        actors_resp = client.get("/api/v1/threat-intel-v2/actors", headers=auth_headers)
        assert actors_resp.status_code == 200
        actors = actors_resp.json()
        assert len(actors) >= 1
        assert "diamond_model" in actors[0]

        # 2. Campaign Heatmaps
        hm_resp = client.get("/api/v1/threat-intel-v2/campaigns/heatmap", headers=auth_headers)
        assert hm_resp.status_code == 200
        heatmaps = hm_resp.json()
        assert len(heatmaps) >= 1

        # 3. Auto-Generate Hunting Queries
        hunt_resp = client.post(
            "/api/v1/threat-intel-v2/hunting/generate-queries",
            json={"actor_name": "Volt Typhoon"},
            headers=auth_headers
        )
        assert hunt_resp.status_code == 200
        queries = hunt_resp.json()
        assert len(queries) >= 2
        assert "query_string" in queries[0]
