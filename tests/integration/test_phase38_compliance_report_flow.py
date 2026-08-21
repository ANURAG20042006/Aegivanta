"""
tests/integration/test_phase38_compliance_report_flow.py
========================================================
Phase 38 Compliance Controls & Report Flow Integration Tests.
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


class TestComplianceReportFlow:
    """Integration tests for compliance controls and generating attestation reports."""

    def test_compliance_controls_and_report_generation(self, client, auth_headers):
        """Test listing controls by framework and generating SHA-256 attested reports."""
        # 1. List Controls
        ctrls_resp = client.get("/api/v1/compliance-detection/compliance-controls?framework=SOC2_TYPE2", headers=auth_headers)
        assert ctrls_resp.status_code == 200
        assert len(ctrls_resp.json()) >= 1

        # 2. List Reports
        reps_resp = client.get("/api/v1/compliance-detection/compliance-reports", headers=auth_headers)
        assert reps_resp.status_code == 200
        assert len(reps_resp.json()) >= 1

        # 3. Generate Report
        gen_resp = client.post(
            "/api/v1/compliance-detection/compliance-reports/generate",
            json={
                "framework": "ISO_27001",
                "generated_by": "lead_compliance_officer"
            },
            headers=auth_headers
        )
        assert gen_resp.status_code == 200
        rep = gen_resp.json()
        assert rep["framework"] == "ISO_27001"
        assert len(rep["auditor_attestation_hash"]) == 64
