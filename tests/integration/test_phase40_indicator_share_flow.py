"""
tests/integration/test_phase40_indicator_share_flow.py
======================================================
Phase 40 Federated Indicator Sharing Flow Integration Tests.
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


class TestIndicatorShareFlow:
    """Integration tests for federated summary, listing nodes/indicators, and sharing an indicator."""

    def test_indicator_share_flow(self, client, auth_headers):
        """Test summary, listing nodes, indicators, and dispatching a new indicator."""
        # 1. Summary
        sum_resp = client.get("/api/v1/federated-threat/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_federated_privacy_score" in sum_resp.json()

        # 2. List Nodes
        nodes_resp = client.get("/api/v1/federated-threat/nodes", headers=auth_headers)
        assert nodes_resp.status_code == 200
        nodes = nodes_resp.json()
        assert len(nodes) >= 1

        # 3. List Indicators
        inds_resp = client.get("/api/v1/federated-threat/indicators", headers=auth_headers)
        assert inds_resp.status_code == 200
        inds = inds_resp.json()
        assert len(inds) >= 1

        # 4. Share Indicator
        share_resp = client.post(
            "/api/v1/federated-threat/indicators/share",
            json={
                "raw_indicator_value": "198.51.100.22",
                "threat_classification": "TOR_EXIT_NODE_C2",
                "differential_privacy_epsilon": 0.5
            },
            headers=auth_headers
        )
        assert share_resp.status_code == 200
        assert len(share_resp.json()["anonymized_indicator_hash"]) == 64
