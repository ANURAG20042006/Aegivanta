"""
tests/integration/test_phase32_cti_feed_flow.py
===============================================
Phase 32 CTI Feeds & Indicator Ledger Integration Tests.
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


class TestCTIFeedIntegrationFlow:
    """Integration tests for STIX/TAXII feed polling and decayed indicator ledger."""

    def test_cti_feed_and_indicator_flow(self, client, auth_headers):
        """Test summary, STIX feeds listing, manual TAXII poll, and indicators."""
        # 1. Summary
        sum_resp = client.get("/api/v1/threat-intel-v2/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_cti_posture_score" in sum_resp.json()

        # 2. List STIX Feeds
        feeds_resp = client.get("/api/v1/threat-intel-v2/feeds", headers=auth_headers)
        assert feeds_resp.status_code == 200
        feeds = feeds_resp.json()
        assert len(feeds) >= 1
        first_feed_id = feeds[0]["id"]

        # 3. Trigger Manual TAXII Poll
        poll_resp = client.post(f"/api/v1/threat-intel-v2/feeds/poll/{first_feed_id}", headers=auth_headers)
        assert poll_resp.status_code == 200
        assert poll_resp.json()["status"] == "POLL_SUCCESSFUL"

        # 4. List CTI Indicators with Decay
        ind_resp = client.get("/api/v1/threat-intel-v2/indicators", headers=auth_headers)
        assert ind_resp.status_code == 200
        assert len(ind_resp.json()) >= 1
