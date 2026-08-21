"""
tests/integration/test_phase34_virtual_patch_flow.py
====================================================
Phase 34 Virtual Patching & Remediation Campaigns Integration Tests.
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


class TestVirtualPatchFlow:
    """Integration tests for Virtual Patch deployment and remediation campaign tracking."""

    def test_virtual_patch_and_campaigns_flow(self, client, auth_headers):
        """Test listing virtual patches, deploying new virtual patch, and listing campaigns."""
        # 1. List Virtual Patches
        vp_resp = client.get("/api/v1/vulnerability-mgmt/virtual-patches", headers=auth_headers)
        assert vp_resp.status_code == 200
        assert len(vp_resp.json()) >= 1

        # 2. Deploy Virtual Patch
        deploy_resp = client.post(
            "/api/v1/vulnerability-mgmt/virtual-patches/deploy",
            json={"cve_id": "CVE-2024-3400", "rule_type": "AWS_WAF"},
            headers=auth_headers
        )
        assert deploy_resp.status_code == 200
        assert deploy_resp.json()["cve_id"] == "CVE-2024-3400"
        assert deploy_resp.json()["status"] == "ACTIVE_ENFORCING"

        # 3. List Remediation Campaigns
        camp_resp = client.get("/api/v1/vulnerability-mgmt/campaigns", headers=auth_headers)
        assert camp_resp.status_code == 200
        assert len(camp_resp.json()) >= 1
