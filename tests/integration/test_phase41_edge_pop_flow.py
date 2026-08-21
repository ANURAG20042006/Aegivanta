"""
tests/integration/test_phase41_edge_pop_flow.py
===============================================
Phase 41 Global Edge PoP & Regional Routes Integration Tests.
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


class TestEdgePoPFlow:
    """Integration tests for edge summary, listing PoPs, and regional routes."""

    def test_edge_pop_flow(self, client, auth_headers):
        """Test summary, listing PoPs and regional WAN routes."""
        # 1. Summary
        sum_resp = client.get("/api/v1/edge-fabric/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_edge_fabric_score" in sum_resp.json()

        # 2. List PoPs
        pops_resp = client.get("/api/v1/edge-fabric/pops", headers=auth_headers)
        assert pops_resp.status_code == 200
        pops = pops_resp.json()
        assert len(pops) >= 1

        # 3. List Routes
        routes_resp = client.get("/api/v1/edge-fabric/routes", headers=auth_headers)
        assert routes_resp.status_code == 200
        routes = routes_resp.json()
        assert len(routes) >= 1
