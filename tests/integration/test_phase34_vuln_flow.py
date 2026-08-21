"""
tests/integration/test_phase34_vuln_flow.py
===========================================
Phase 34 RBVM Vulnerabilities & Asset SLA Integration Tests.
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


class TestRBVMVulnFlow:
    """Integration tests for RBVM summary, vulnerabilities listing, and asset exposures."""

    def test_vulnerability_and_asset_sla_flow(self, client, auth_headers):
        """Test summary, vulnerabilities with EPSS, asset exposures, and EPSS distribution."""
        # 1. Summary
        sum_resp = client.get("/api/v1/vulnerability-mgmt/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_rbvm_posture_score" in sum_resp.json()

        # 2. List Prioritized Vulnerabilities
        vuln_resp = client.get("/api/v1/vulnerability-mgmt/vulnerabilities", headers=auth_headers)
        assert vuln_resp.status_code == 200
        vulns = vuln_resp.json()
        assert len(vulns) >= 1
        assert "epss_probability" in vulns[0]

        # 3. List Asset Exposures & SLAs
        asset_resp = client.get("/api/v1/vulnerability-mgmt/asset-exposures", headers=auth_headers)
        assert asset_resp.status_code == 200
        assert len(asset_resp.json()) >= 1

        # 4. EPSS Distribution Buckets
        dist_resp = client.get("/api/v1/vulnerability-mgmt/epss-distribution", headers=auth_headers)
        assert dist_resp.status_code == 200
        assert len(dist_resp.json()) >= 4
