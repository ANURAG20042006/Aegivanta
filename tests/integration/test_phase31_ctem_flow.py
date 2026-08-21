"""
tests/integration/test_phase31_ctem_flow.py
===========================================
Phase 31 CTEM Exposure & Dark Web Intelligence Integration Tests.
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


class TestCTEMIntegrationFlow:
    """Integration tests for Dark Web Credential Leaks, Brand Typosquats, and CTEM Prioritization."""

    def test_darkweb_brand_and_ctem_prioritization_flow(self, client, auth_headers):
        """Test darkweb credential leaks, brand alerts, and CTEM prioritized exposures."""
        # 1. Dark Web Credential Leaks
        dw_resp = client.get("/api/v1/attack-surface/darkweb/credentials", headers=auth_headers)
        assert dw_resp.status_code == 200
        leaks = dw_resp.json()
        assert len(leaks) >= 1

        # 2. Brand Typosquats
        brand_resp = client.get("/api/v1/attack-surface/brand/typosquats", headers=auth_headers)
        assert brand_resp.status_code == 200
        alerts = brand_resp.json()
        assert len(alerts) >= 1

        # 3. CTEM Prioritized Exposures
        ctem_resp = client.get("/api/v1/attack-surface/ctem/prioritized-exposures", headers=auth_headers)
        assert ctem_resp.status_code == 200
        exposures = ctem_resp.json()
        assert len(exposures) >= 1
        assert "epss_percentile" in exposures[0]
