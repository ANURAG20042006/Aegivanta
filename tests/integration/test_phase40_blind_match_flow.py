"""
tests/integration/test_phase40_blind_match_flow.py
==================================================
Phase 40 Homomorphic Blind Match Flow Integration Tests.
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


class TestBlindMatchFlow:
    """Integration tests for executing encrypted zero-knowledge homomorphic blind matching."""

    def test_blind_match_flow(self, client, auth_headers):
        """Test blind match against known seed indicator and unknown indicator."""
        # 1. Blind Match Query against existing indicator
        match_resp = client.post(
            "/api/v1/federated-threat/blind-match",
            json={
                "target_ioc_query": "APT29_COZYBEAR_C2_HOST"
            },
            headers=auth_headers
        )
        assert match_resp.status_code == 200
        data = match_resp.json()
        assert data["blind_match_status"] == "BLIND_MATCH_FOUND"
        assert len(data["encrypted_query_hash"]) == 64
        assert data["matched_threat_classification"] == "APT_C2_INFRASTRUCTURE"

        # 2. Blind Match Query against non-existent indicator
        no_match_resp = client.post(
            "/api/v1/federated-threat/blind-match",
            json={
                "target_ioc_query": "NON_EXISTENT_BENIGN_STRING_XYZ_999"
            },
            headers=auth_headers
        )
        assert no_match_resp.status_code == 200
        assert no_match_resp.json()["blind_match_status"] == "NO_MATCH"
