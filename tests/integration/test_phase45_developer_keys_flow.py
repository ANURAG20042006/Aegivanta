"""
tests/integration/test_phase45_developer_keys_flow.py
=====================================================
Phase 45 Developer API Key Flow Integration Tests.
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


class TestDeveloperKeysFlow:
    """Integration tests for summary, listing keys, and generating a new developer API key."""

    def test_developer_keys_flow(self, client, auth_headers):
        """Test summary, listing keys, and key creation."""
        # 1. Summary
        sum_resp = client.get("/api/v1/developer/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_developer_score" in sum_resp.json()

        # 2. List Keys
        keys_resp = client.get("/api/v1/developer/keys", headers=auth_headers)
        assert keys_resp.status_code == 200
        keys = keys_resp.json()
        assert len(keys) >= 1

        # 3. Create Key
        create_resp = client.post(
            "/api/v1/developer/keys",
            json={
                "key_name": "Custom SOAR Pipeline Integration Key",
                "scopes": "telemetry:read,alerts:write,soar:execute",
                "rate_limit_rpm": 2000
            },
            headers=auth_headers
        )
        assert create_resp.status_code == 200
        data = create_resp.json()
        assert "raw_api_key" in data
        assert data["raw_api_key"].startswith("aeg_live_")
        assert data["rate_limit_rpm"] == 2000
