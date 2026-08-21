"""
tests/integration/test_phase39_forecast_flow.py
===============================================
Phase 39 Predictive Intelligence & Threat Forecast Flow Integration Tests.
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


class TestForecastFlow:
    """Integration tests for summary, forecast listing, and custom forecast generation."""

    def test_forecast_flow(self, client, auth_headers):
        """Test predictive summary, listing forecasts by horizon, and generating forecasts."""
        # 1. Summary
        sum_resp = client.get("/api/v1/predictive-intel/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_predictive_posture_score" in sum_resp.json()

        # 2. List Forecasts
        fcs_resp = client.get("/api/v1/predictive-intel/forecasts?horizon=30_DAYS", headers=auth_headers)
        assert fcs_resp.status_code == 200
        fcs = fcs_resp.json()
        assert len(fcs) >= 1

        # 3. Generate Forecast
        gen_resp = client.post(
            "/api/v1/predictive-intel/forecasts/generate",
            json={
                "threat_vector_title": "AI System Prompt Leakage via Prompt Injection",
                "target_asset_category": "Internal LLM RAG Gateways",
                "forecast_horizon": "30_DAYS"
            },
            headers=auth_headers
        )
        assert gen_resp.status_code == 200
        assert gen_resp.json()["threat_vector_title"] == "AI System Prompt Leakage via Prompt Injection"
