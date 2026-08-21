"""
tests/integration/test_phase33_canary_flow.py
=============================================
Phase 33 Canary Token Generation & Trigger Webhook Integration Tests.
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


class TestCanaryFlow:
    """Integration tests for Canary token generation and trip triggering."""

    def test_canary_token_generation_and_trigger_flow(self, client, auth_headers):
        """Test generating a canary token, listing tokens, and triggering trip webhook."""
        # 1. Generate Token
        gen_resp = client.post(
            "/api/v1/deception/canaries/generate",
            json={
                "token_type": "AWS_API_KEY",
                "token_name": "vault-admin-canary-key",
                "placement_description": "Placed in /root/.aws/credentials on Bastion 02"
            },
            headers=auth_headers
        )
        assert gen_resp.status_code == 200
        token_id = gen_resp.json()["id"]

        # 2. List Tokens
        canaries_resp = client.get("/api/v1/deception/canaries", headers=auth_headers)
        assert canaries_resp.status_code == 200
        tokens = canaries_resp.json()
        assert any(t["id"] == token_id for t in tokens)

        # 3. Simulate Canary Trip Trigger
        trig_resp = client.post(
            f"/api/v1/deception/canaries/trigger/{token_id}",
            json={"source_ip": "198.51.100.77"},
            headers=auth_headers
        )
        assert trig_resp.status_code == 200
        assert trig_resp.json()["status"] == "CANARY_TRIGGERED"
        assert trig_resp.json()["times_triggered"] >= 1
