"""
tests/integration/test_phase26_soc_flow.py
==========================================
Phase 26 SOC Operations & Scorecard Integration Flow Tests.
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


class TestPhase26SOCFlow:
    """Integration flow for Phase 26 SOC Command Center APIs."""

    def test_get_security_scorecard_flow(self, client, auth_headers):
        """GET /api/v1/security/scorecard returns valid scorecard structure."""
        resp = client.get("/api/v1/security/scorecard", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "overall_security_score" in data
        assert "category_scores" in data
        assert 0.0 <= data["overall_security_score"] <= 100.0

    def test_continuous_validation_flow(self, client, auth_headers):
        """GET & POST /api/v1/security/continuous-validation flow."""
        get_resp = client.get("/api/v1/security/continuous-validation", headers=auth_headers)
        assert get_resp.status_code == 200
        val_data = get_resp.json()
        assert "overall_score" in val_data
        assert "checks" in val_data

        run_resp = client.post("/api/v1/security/continuous-validation/run", headers=auth_headers)
        assert run_resp.status_code == 200
        run_data = run_resp.json()
        assert run_data["total_checks"] == 16

    def test_sre_health_and_slo_flow(self, client, auth_headers):
        """SRE health, SLO and Error budget endpoints flow."""
        h_resp = client.get("/api/v1/sre/health", headers=auth_headers)
        assert h_resp.status_code == 200
        assert h_resp.json()["status"] == "HEALTHY"

        slo_resp = client.get("/api/v1/sre/slo", headers=auth_headers)
        assert slo_resp.status_code == 200
        assert slo_resp.json()["overall_compliance"] is True

        eb_resp = client.get("/api/v1/sre/error-budget", headers=auth_headers)
        assert eb_resp.status_code == 200
        assert eb_resp.json()["remaining_budget_pct"] > 0.0
