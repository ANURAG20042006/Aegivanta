"""
tests/integration/test_phase41_policy_deploy_flow.py
====================================================
Phase 41 Edge Inspection Policy Deploy Flow Integration Tests.
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


class TestPolicyDeployFlow:
    """Integration tests for listing and deploying edge inspection policies."""

    def test_policy_deploy_flow(self, client, auth_headers):
        """Test listing policies and deploying a new edge policy."""
        # 1. List Policies
        pols_resp = client.get("/api/v1/edge-fabric/policies", headers=auth_headers)
        assert pols_resp.status_code == 200
        pols = pols_resp.json()
        assert len(pols) >= 1

        # 2. Deploy Policy
        create_resp = client.post(
            "/api/v1/edge-fabric/policies",
            json={
                "policy_name": "Edge TLS 1.3 Anti-Replay Inspection",
                "inspection_mode": "INLINE_BLOCK",
                "edge_rate_limit_rps": 75000,
                "geo_fence_action": "CHALLENGE"
            },
            headers=auth_headers
        )
        assert create_resp.status_code == 200
        data = create_resp.json()
        assert data["policy_name"] == "Edge TLS 1.3 Anti-Replay Inspection"
        assert data["inspection_mode"] == "INLINE_BLOCK"
        assert data["edge_rate_limit_rps"] == 75000
