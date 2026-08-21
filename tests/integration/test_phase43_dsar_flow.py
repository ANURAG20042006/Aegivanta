"""
tests/integration/test_phase43_dsar_flow.py
===========================================
Phase 43 DSAR Privacy Request Flow Integration Tests.
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


class TestDSARFlow:
    """Integration tests for submitting and reading DSAR requests."""

    def test_dsar_flow(self, client, auth_headers):
        """Test submitting and querying DSAR privacy requests."""
        # 1. Submit DSAR Request
        req_resp = client.post(
            "/api/v1/governance-dsar/requests",
            json={
                "requester_email": "sar-auditor@enterprise.com",
                "request_type": "RIGHT_OF_ACCESS_EXPORT"
            },
            headers=auth_headers
        )
        assert req_resp.status_code == 200
        data = req_resp.json()
        assert data["status"] == "COMPLETED"
        assert len(data["completion_certificate_hash"]) == 64

        # 2. List Requests
        list_resp = client.get("/api/v1/governance-dsar/requests", headers=auth_headers)
        assert list_resp.status_code == 200
        reqs = list_resp.json()
        assert len(reqs) >= 1
