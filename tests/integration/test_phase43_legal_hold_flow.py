"""
tests/integration/test_phase43_legal_hold_flow.py
=================================================
Phase 43 Legal Hold Flow Integration Tests.
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


class TestLegalHoldFlow:
    """Integration tests for summary, listing lineage, and issuing a legal hold."""

    def test_legal_hold_flow(self, client, auth_headers):
        """Test summary, lineage, and creating a legal hold order."""
        # 1. Summary
        sum_resp = client.get("/api/v1/governance-dsar/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_governance_score" in sum_resp.json()

        # 2. List Lineage
        lin_resp = client.get("/api/v1/governance-dsar/lineage", headers=auth_headers)
        assert lin_resp.status_code == 200
        lineage = lin_resp.json()
        assert len(lineage) >= 1

        # 3. Create Legal Hold
        hold_resp = client.post(
            "/api/v1/governance-dsar/legal-holds",
            json={
                "matter_reference": "MATTER-2026-SEC-INVESTIGATION-04",
                "custodian_name": "Chief Legal Officer",
                "scope_pattern": "CASE_FORENSICS_APT29_*"
            },
            headers=auth_headers
        )
        assert hold_resp.status_code == 200
        data = hold_resp.json()
        assert data["matter_reference"] == "MATTER-2026-SEC-INVESTIGATION-04"
        assert data["status"] == "ACTIVE_HOLD"
