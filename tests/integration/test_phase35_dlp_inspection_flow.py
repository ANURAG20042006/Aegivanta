"""
tests/integration/test_phase35_dlp_inspection_flow.py
=====================================================
Phase 35 DLP Policies & Real-Time Inspection Flow Integration Tests.
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


class TestDLPInspectionFlow:
    """Integration tests for DLP summary, policies, real-time payload inspection, and incidents."""

    def test_dlp_inspection_and_incidents_flow(self, client, auth_headers):
        """Test DLP summary, policies listing, sandbox payload inspection, and incidents listing."""
        # 1. Summary
        sum_resp = client.get("/api/v1/dlp-security/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_dlp_posture_score" in sum_resp.json()

        # 2. List Policies
        pol_resp = client.get("/api/v1/dlp-security/policies", headers=auth_headers)
        assert pol_resp.status_code == 200
        assert len(pol_resp.json()) >= 1

        # 3. Real-Time Inspection Sandbox
        payload = {"payload_text": "Customer PAN 4111 1111 1111 1111 with SSN 123-45-6789"}
        insp_resp = client.post("/api/v1/dlp-security/inspect", json=payload, headers=auth_headers)
        assert insp_resp.status_code == 200
        data = insp_resp.json()
        assert data["is_violating"] is True
        assert "4111-XXXX-XXXX-1111" in data["sanitized_payload"]

        # 4. List Incidents
        inc_resp = client.get("/api/v1/dlp-security/incidents", headers=auth_headers)
        assert inc_resp.status_code == 200
        assert len(inc_resp.json()) >= 1
