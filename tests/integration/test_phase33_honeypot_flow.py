"""
tests/integration/test_phase33_honeypot_flow.py
===============================================
Phase 33 Honeypot Fleet & Decoy Lifecycle Integration Tests.
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


class TestHoneypotFlow:
    """Integration tests for Honeypot fleet listing and decoy deployment."""

    def test_honeypot_deployment_and_listing_flow(self, client, auth_headers):
        """Test summary, listing honeypots, deploying a new honeypot decoy, and interaction events."""
        # 1. Summary
        sum_resp = client.get("/api/v1/deception/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_deception_readiness_score" in sum_resp.json()

        # 2. List Honeypots
        pots_resp = client.get("/api/v1/deception/honeypots", headers=auth_headers)
        assert pots_resp.status_code == 200
        assert len(pots_resp.json()) >= 1

        # 3. Deploy New Honeypot Decoy
        deploy_resp = client.post(
            "/api/v1/deception/honeypots/deploy",
            json={
                "node_name": "decoy-database-postgres-01",
                "decoy_type": "DATABASE",
                "internal_ip": "10.0.12.99",
                "vlan_segment": "DECEPTION-VLAN-100"
            },
            headers=auth_headers
        )
        assert deploy_resp.status_code == 200
        assert deploy_resp.json()["node_name"] == "decoy-database-postgres-01"

        # 4. List Interactions
        intx_resp = client.get("/api/v1/deception/interactions", headers=auth_headers)
        assert intx_resp.status_code == 200
        assert len(intx_resp.json()) >= 1

        # 5. List Endpoint Lures
        lures_resp = client.get("/api/v1/deception/endpoint-lures", headers=auth_headers)
        assert lures_resp.status_code == 200
        assert len(lures_resp.json()) >= 1
