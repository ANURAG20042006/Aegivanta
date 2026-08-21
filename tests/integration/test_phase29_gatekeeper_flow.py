"""
tests/integration/test_phase29_gatekeeper_flow.py
=================================================
Phase 29 CI/CD Gatekeeper & Secret Scanner Integration Tests.
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


class TestGatekeeperIntegrationFlow:
    """Integration tests for CI/CD pipeline gate evaluation and secret scanning."""

    def test_gate_evaluation_and_secret_scanning_flow(self, client, auth_headers):
        """Test gate listing, deployment evaluation, and secret scanning."""
        # 1. List Gates
        gates_resp = client.get("/api/v1/supply-chain/gates", headers=auth_headers)
        assert gates_resp.status_code == 200
        assert len(gates_resp.json()) >= 1

        # 2. Evaluate Clean Gate -> PASSED
        clean_eval = client.post(
            "/api/v1/supply-chain/gates/evaluate",
            json={
                "target_environment": "PRODUCTION",
                "critical_cves": 0,
                "high_cves": 0,
                "has_slsa_level_3": True,
                "has_copyleft_license": False,
                "has_secrets_detected": False
            },
            headers=auth_headers
        )
        assert clean_eval.status_code == 200
        assert clean_eval.json()["is_passed"] is True
        assert clean_eval.json()["gate_status"] == "PASSED"

        # 3. Evaluate Gate with Violations -> BLOCKED
        dirty_eval = client.post(
            "/api/v1/supply-chain/gates/evaluate",
            json={
                "target_environment": "PRODUCTION",
                "critical_cves": 2,
                "high_cves": 5,
                "has_slsa_level_3": False,
                "has_copyleft_license": True,
                "has_secrets_detected": True
            },
            headers=auth_headers
        )
        assert dirty_eval.status_code == 200
        assert dirty_eval.json()["is_passed"] is False
        assert dirty_eval.json()["gate_status"] == "BLOCKED"
        assert dirty_eval.json()["violations_count"] >= 3

        # 4. Secret Scan endpoint
        sec_resp = client.post(
            "/api/v1/supply-chain/secrets/scan",
            json={"file_content": "const key = 'AKIA1234567890EXAMPLE';"}
        )
        assert sec_resp.status_code == 200
        assert sec_resp.json()["is_clean"] is False
        assert sec_resp.json()["secrets_detected_count"] >= 1
