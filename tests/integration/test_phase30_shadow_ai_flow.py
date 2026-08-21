"""
tests/integration/test_phase30_shadow_ai_flow.py
================================================
Phase 30 Shadow AI & Vector DB Integration Tests.
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


class TestShadowAIIntegrationFlow:
    """Integration tests for Shadow AI tool management and Vector DB audits."""

    def test_shadow_ai_and_vectordb_flow(self, client, auth_headers):
        """Test shadow AI discovery list, blocking toggle, and Vector DB collection scan."""
        # 1. List Shadow AI tools
        shadow_resp = client.get("/api/v1/llm-security/shadow-ai", headers=auth_headers)
        assert shadow_resp.status_code == 200
        tools = shadow_resp.json()
        assert len(tools) >= 1
        first_id = tools[0]["id"]

        # 2. Block Shadow AI tool
        blk_resp = client.post(
            f"/api/v1/llm-security/shadow-ai/block/{first_id}",
            json={"block": True},
            headers=auth_headers
        )
        assert blk_resp.status_code == 200
        assert blk_resp.json()["is_blocked"] is True

        # 3. Vector DB Audits
        v_list = client.get("/api/v1/llm-security/vectordb/audits", headers=auth_headers)
        assert v_list.status_code == 200
        assert len(v_list.json()) >= 1

        # 4. Scan new Vector DB collection
        scan_resp = client.post(
            "/api/v1/llm-security/vectordb/scan",
            json={
                "db_type": "PINECONE",
                "collection_name": "agentic_rag_index_v2",
                "total_embeddings": 50000
            },
            headers=auth_headers
        )
        assert scan_resp.status_code == 200
        assert scan_resp.json()["audit_status"] == "SECURE"
