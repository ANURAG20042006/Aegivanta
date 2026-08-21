"""
tests/integration/test_phase42_failover_flow.py
===============================================
Phase 42 Regional Failover Trigger & Execution Flow Integration Tests.
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


class TestFailoverFlow:
    """Integration tests for triggering failover and reading historical failover events."""

    def test_failover_flow(self, client, auth_headers):
        """Test triggering a regional failover switchover and querying events."""
        # 1. Trigger Failover
        fo_resp = client.post(
            "/api/v1/multi-region/failover",
            json={
                "source_region": "US_EAST_PRIMARY",
                "target_region": "EU_WEST_SECONDARY",
                "trigger_type": "OPERATOR_INITIATED"
            },
            headers=auth_headers
        )
        assert fo_resp.status_code == 200
        data = fo_resp.json()
        assert data["status"] == "SUCCESS"
        assert data["source_failing_region"] == "US_EAST_PRIMARY"
        assert data["target_failover_region"] == "EU_WEST_SECONDARY"

        # 2. List Failover Events
        evts_resp = client.get("/api/v1/multi-region/failover-events", headers=auth_headers)
        assert evts_resp.status_code == 200
        evts = evts_resp.json()
        assert len(evts) >= 1
