"""
tests/integration/test_phase28_itdr_flow.py
===========================================
Phase 28 ITDR & Continuous Zero Trust Auth Integration Flow Tests.
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


class TestITDRIntegrationFlow:
    """Integration tests for ITDR detections, simulations, and Zero Trust continuous auth."""

    def test_itdr_and_zero_trust_flow(self, client, auth_headers):
        """Test ITDR threat simulation and Zero Trust continuous evaluation."""
        # 1. Summary
        sum_resp = client.get("/api/v1/iam/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_identity_trust_score" in sum_resp.json()

        # 2. Simulate ITDR attack
        sim_resp = client.post(
            "/api/v1/iam/itdr/simulate-attack",
            json={
                "threat_type": "MFA_FATIGUE",
                "target_username": "sarah.connor@aegivanta.io",
                "source_ip": "198.51.100.99"
            },
            headers=auth_headers
        )
        assert sim_resp.status_code == 200
        assert sim_resp.json()["status"] == "DETECTED_AND_BLOCKED"

        # 3. Continuous Zero Trust evaluation
        zt_resp = client.post(
            "/api/v1/iam/zero-trust/evaluate-session",
            json={
                "username": "sarah.connor@aegivanta.io",
                "identity_risk_score": 15.0,
                "device_trust_score": 90.0,
                "resource_criticality": "HIGH",
                "is_known_location": True,
                "is_managed_device": True
            },
            headers=auth_headers
        )
        assert zt_resp.status_code == 200
        assert zt_resp.json()["verdict"] in ("ALLOW", "STEP_UP_MFA")

        # 4. List Passkeys and Scorecards
        pk_resp = client.get("/api/v1/iam/passkeys", headers=auth_headers)
        assert pk_resp.status_code == 200
        assert len(pk_resp.json()) >= 1

        sc_resp = client.get("/api/v1/iam/governance/scorecards", headers=auth_headers)
        assert sc_resp.status_code == 200
        assert len(sc_resp.json()) >= 1
