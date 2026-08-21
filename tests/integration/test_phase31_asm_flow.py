"""
tests/integration/test_phase31_asm_flow.py
==========================================
Phase 31 Attack Surface Management (ASM) Flow Integration Tests.
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


class TestASMIntegrationFlow:
    """Integration tests for External Recon, Asset Discovery, and Dangling DNS APIs."""

    def test_asm_recon_and_asset_inventory_flow(self, client, auth_headers):
        """Test summary, asset list, domain enrollment, and dangling DNS endpoints."""
        # 1. Get ASM Summary
        sum_resp = client.get("/api/v1/attack-surface/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_asm_posture_score" in sum_resp.json()

        # 2. List External Assets
        assets_resp = client.get("/api/v1/attack-surface/assets", headers=auth_headers)
        assert assets_resp.status_code == 200
        assets = assets_resp.json()
        assert len(assets) >= 1

        # 3. Enroll / Discover New External Domain
        enroll_resp = client.post(
            "/api/v1/attack-surface/assets/discover",
            json={
                "domain_name": "portal-stage.aegivanta.io",
                "cloud_provider": "AWS"
            },
            headers=auth_headers
        )
        assert enroll_resp.status_code == 200
        assert enroll_resp.json()["fqdn_or_ip"] == "portal-stage.aegivanta.io"

        # 4. List Dangling DNS Records
        dd_resp = client.get("/api/v1/attack-surface/dangling-dns", headers=auth_headers)
        assert dd_resp.status_code == 200
        assert len(dd_resp.json()) >= 1
