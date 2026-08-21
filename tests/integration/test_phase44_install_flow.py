"""
tests/integration/test_phase44_install_flow.py
==============================================
Phase 44 Extension Package Install & Hot-Reload Flow Integration Tests.
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


class TestPackageInstallFlow:
    """Integration tests for installing and listing tenant security extensions."""

    def test_package_install_flow(self, client, auth_headers):
        """Test installing and querying extensions."""
        # 1. Install Extension
        inst_resp = client.post(
            "/api/v1/marketplace/install",
            json={
                "package_id": "pkg-test-01",
                "package_name": "Test Hot-Reload Detection Module",
                "version": "1.0.0"
            },
            headers=auth_headers
        )
        assert inst_resp.status_code == 200
        data = inst_resp.json()
        assert data["status"] == "HOT_RELOADED_ACTIVE"

        # 2. List Installed
        list_resp = client.get("/api/v1/marketplace/installed", headers=auth_headers)
        assert list_resp.status_code == 200
        installed = list_resp.json()
        assert len(installed) >= 1
