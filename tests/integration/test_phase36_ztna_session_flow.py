"""
tests/integration/test_phase36_ztna_session_flow.py
===================================================
Phase 36 ZTNA Session & Connector Flow Integration Tests.
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


class TestZTNASessionFlow:
    """Integration tests for ZTNA summary, connectors, and client sessions."""

    def test_ztna_connectors_and_sessions_flow(self, client, auth_headers):
        """Test summary, connector listing, session listing, and session termination."""
        # 1. Summary
        sum_resp = client.get("/api/v1/microsegmentation/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_ztna_posture_score" in sum_resp.json()

        # 2. List Connectors
        conn_resp = client.get("/api/v1/microsegmentation/connectors", headers=auth_headers)
        assert conn_resp.status_code == 200
        assert len(conn_resp.json()) >= 1

        # 3. List Sessions
        sess_resp = client.get("/api/v1/microsegmentation/sessions", headers=auth_headers)
        assert sess_resp.status_code == 200
        sessions = sess_resp.json()
        assert len(sessions) >= 1
        sess_id = sessions[0]["id"]

        # 4. Terminate Session
        term_resp = client.post(
            "/api/v1/microsegmentation/sessions/terminate",
            json={"session_id": sess_id},
            headers=auth_headers
        )
        assert term_resp.status_code == 200
        assert term_resp.json()["success"] is True
