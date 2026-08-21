"""
tests/integration/test_phase44_catalog_flow.py
==============================================
Phase 44 Marketplace Catalog Flow Integration Tests.
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


class TestMarketplaceCatalogFlow:
    """Integration tests for summary, listing packages, and publishing a package."""

    def test_marketplace_catalog_flow(self, client, auth_headers):
        """Test summary, package search, and package publishing."""
        # 1. Summary
        sum_resp = client.get("/api/v1/marketplace/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_ecosystem_score" in sum_resp.json()

        # 2. List Packages
        pkgs_resp = client.get("/api/v1/marketplace/packages", headers=auth_headers)
        assert pkgs_resp.status_code == 200
        packages = pkgs_resp.json()
        assert len(packages) >= 1

        # 3. Publish Package
        pub_resp = client.post(
            "/api/v1/marketplace/publish",
            json={
                "package_name": "Autonomous Kubernetes Pod Quarantine Playbook",
                "package_type": "SOAR_PLAYBOOK",
                "version": "1.0.0",
                "author": "Enterprise DevSecOps"
            },
            headers=auth_headers
        )
        assert pub_resp.status_code == 200
        assert pub_resp.json()["package_name"] == "Autonomous Kubernetes Pod Quarantine Playbook"
