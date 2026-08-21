"""
tests/integration/test_phase37_ueba_risk_flow.py
================================================
Phase 37 UEBA Profiles & Insider Threats Integration Tests.
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


class TestUEBARiskFlow:
    """Integration tests for UEBA profiles and insider threats listing."""

    def test_ueba_profiles_and_insider_threats(self, client, auth_headers):
        """Test listing profiles, investigations, and insider threat indicators."""
        # 1. List UEBA Profiles
        prof_resp = client.get("/api/v1/ai-soc-ueba/profiles", headers=auth_headers)
        assert prof_resp.status_code == 200
        assert len(prof_resp.json()) >= 1

        # 2. List Insider Threat Indicators
        threat_resp = client.get("/api/v1/ai-soc-ueba/insider-threats", headers=auth_headers)
        assert threat_resp.status_code == 200
        assert len(threat_resp.json()) >= 1

        # 3. List Investigations
        inv_resp = client.get("/api/v1/ai-soc-ueba/investigations", headers=auth_headers)
        assert inv_resp.status_code == 200
        assert len(inv_resp.json()) >= 1
