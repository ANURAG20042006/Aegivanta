"""
tests/integration/test_phase35_tokenization_flow.py
===================================================
Phase 35 Tokenization Vault & DSPM Shadow Data Integration Tests.
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


class TestTokenizationFlow:
    """Integration tests for Tokenization Vault, Detokenization, and DSPM Shadow Data."""

    def test_tokenization_and_shadow_data_flow(self, client, auth_headers):
        """Test listing tokens, tokenizing new record, detokenizing with admin role, and listing shadow data."""
        # 1. List Tokens
        tkn_resp = client.get("/api/v1/dlp-security/tokens", headers=auth_headers)
        assert tkn_resp.status_code == 200
        assert len(tkn_resp.json()) >= 1

        # 2. Tokenize new record
        tok_resp = client.post(
            "/api/v1/dlp-security/tokens/tokenize",
            json={"raw_value": "4111-9824-7712-1111", "token_format": "FPE_CREDIT_CARD"},
            headers=auth_headers
        )
        assert tok_resp.status_code == 200
        token_data = tok_resp.json()
        assert "token_identifier" in token_data
        token_id = token_data["token_identifier"]

        # 3. Detokenize record
        detok_resp = client.post(
            "/api/v1/dlp-security/tokens/detokenize",
            json={"token_identifier": token_id, "requestor_role": "admin"},
            headers=auth_headers
        )
        assert detok_resp.status_code == 200
        assert detok_resp.json()["authorized"] is True

        # 4. List Shadow Data Stores
        shdw_resp = client.get("/api/v1/dlp-security/shadow-data", headers=auth_headers)
        assert shdw_resp.status_code == 200
        assert len(shdw_resp.json()) >= 1
