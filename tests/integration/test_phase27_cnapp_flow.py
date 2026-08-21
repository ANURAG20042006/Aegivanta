"""
tests/integration/test_phase27_cnapp_flow.py
============================================
Phase 27 CNAPP Posture & Multi-Cloud Connectors Integration Flow Tests.
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


class TestCNAPPIntegrationFlow:
    """Integration tests for CNAPP posture and cloud account APIs."""

    def test_cnapp_summary_flow(self, client, auth_headers):
        """GET /api/v1/cloud-security/cnapp/summary returns 200 and posture metrics."""
        resp = client.get("/api/v1/cloud-security/cnapp/summary", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "overall_cnapp_score" in data
        assert "pillar_scores" in data
        assert 0.0 <= data["overall_cnapp_score"] <= 100.0

    def test_cloud_accounts_flow(self, client, auth_headers):
        """List and connect cloud account flow."""
        # 1. List accounts
        list_resp = client.get("/api/v1/cloud-security/accounts", headers=auth_headers)
        assert list_resp.status_code == 200
        accounts = list_resp.json()
        assert len(accounts) >= 1

        # 2. Connect new account
        conn_resp = client.post(
            "/api/v1/cloud-security/accounts",
            json={
                "provider": "AWS",
                "account_name": "Integration-Test-AWS",
                "account_identifier": "987654321098",
                "auth_type": "ASSUME_ROLE",
                "credentials": {"role_arn": "arn:aws:iam::987654321098:role/Test"}
            },
            headers=auth_headers
        )
        assert conn_resp.status_code == 200
        acc_id = conn_resp.json()["id"]

        # 3. Sync account
        sync_resp = client.post(f"/api/v1/cloud-security/accounts/{acc_id}/sync", headers=auth_headers)
        assert sync_resp.status_code == 200
        assert sync_resp.json()["sync_status"] == "SYNCED"
