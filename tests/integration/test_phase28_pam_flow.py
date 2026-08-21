"""
tests/integration/test_phase28_pam_flow.py
==========================================
Phase 28 PAM & JIT Elevation Integration Flow Tests.
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


class TestPAMIntegrationFlow:
    """Integration tests for PAM JIT elevation workflows."""

    def test_pam_jit_lifecycle_flow(self, client, auth_headers):
        """Request elevation, list, approve, and revoke JIT session."""
        # 1. Request elevation
        req_resp = client.post(
            "/api/v1/iam/pam/request-elevation",
            json={
                "user_id": "usr-test-01",
                "username": "sarah.connor@aegivanta.io",
                "target_role": "CLUSTER_ADMIN",
                "target_resource": "PROD_K8S_PRIMARY",
                "justification": "Integration testing JIT elevation",
                "duration_minutes": 30
            },
            headers=auth_headers
        )
        assert req_resp.status_code == 200
        elev_id = req_resp.json()["id"]
        assert req_resp.json()["status"] == "PENDING"

        # 2. List elevations
        list_resp = client.get("/api/v1/iam/pam/elevations", headers=auth_headers)
        assert list_resp.status_code == 200
        assert any(e["id"] == elev_id for e in list_resp.json())

        # 3. Approve elevation
        appr_resp = client.post(f"/api/v1/iam/pam/approve/{elev_id}", headers=auth_headers)
        assert appr_resp.status_code == 200
        assert appr_resp.json()["status"] == "ACTIVE"

        # 4. Revoke elevation
        rev_resp = client.post(f"/api/v1/iam/pam/revoke/{elev_id}", headers=auth_headers)
        assert rev_resp.status_code == 200
        assert rev_resp.json()["status"] == "REVOKED"
