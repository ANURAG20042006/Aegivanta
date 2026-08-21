"""
tests/integration/test_phase37_investigation_flow.py
====================================================
Phase 37 AI SOC Autonomous Investigation & Decision Flow Integration Tests.
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


class TestInvestigationFlow:
    """Integration tests for AI SOC summary, triggering investigation, and approving containment."""

    def test_ai_soc_investigation_and_approval_flow(self, client, auth_headers):
        """Test summary, trigger autonomous investigation, and action approval."""
        # 1. Summary
        sum_resp = client.get("/api/v1/ai-soc-ueba/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_ai_soc_autonomy_score" in sum_resp.json()

        # 2. Trigger Investigation
        trig_resp = client.post(
            "/api/v1/ai-soc-ueba/investigations/trigger",
            json={
                "alert_id": "ALT-TEST-9921",
                "alert_title": "Automated Test S3 Data Dump"
            },
            headers=auth_headers
        )
        assert trig_resp.status_code == 200
        inv = trig_resp.json()
        assert "id" in inv
        inv_id = inv["id"]

        # 3. Approve Action
        appr_resp = client.post(
            "/api/v1/ai-soc-ueba/investigations/approve-action",
            json={
                "investigation_id": inv_id,
                "action": "Isolate Endpoint & Reset Token",
                "acted_by": "lead_commander"
            },
            headers=auth_headers
        )
        assert appr_resp.status_code == 200
        assert appr_resp.json()["approval_status"] == "APPROVED"

        # 4. List Decision Audits
        audit_resp = client.get("/api/v1/ai-soc-ueba/decision-audits", headers=auth_headers)
        assert audit_resp.status_code == 200
        assert len(audit_resp.json()) >= 1
