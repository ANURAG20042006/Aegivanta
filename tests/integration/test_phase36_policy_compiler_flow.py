"""
tests/integration/test_phase36_policy_compiler_flow.py
======================================================
Phase 36 Microsegmentation Policies & Flow Graph Integration Tests.
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


class TestPolicyCompilerFlow:
    """Integration tests for creating policies, lateral alerts, and network flow mesh."""

    def test_policy_creation_and_mesh_flow(self, client, auth_headers):
        """Test listing policies, creating new policy, lateral alerts, and network flow mesh."""
        # 1. List Policies
        pols_resp = client.get("/api/v1/microsegmentation/policies", headers=auth_headers)
        assert pols_resp.status_code == 200
        assert len(pols_resp.json()) >= 1

        # 2. Create Policy
        new_pol = {
            "policy_name": "Isolate Kubernetes Backend",
            "source_segment": "K8S_FRONTEND",
            "destination_segment": "CORE_DATABASE_CLUSTER",
            "protocol_port": "TCP/5432",
            "enforcement_action": "ALLOW_ENCRYPTED_TUNNEL",
            "min_device_trust_score": 80
        }
        create_resp = client.post("/api/v1/microsegmentation/policies", json=new_pol, headers=auth_headers)
        assert create_resp.status_code == 200
        assert create_resp.json()["policy_name"] == "Isolate Kubernetes Backend"

        # 3. List Lateral Movement Alerts
        alert_resp = client.get("/api/v1/microsegmentation/lateral-alerts", headers=auth_headers)
        assert alert_resp.status_code == 200
        assert len(alert_resp.json()) >= 1

        # 4. Get Network Flow Graph
        mesh_resp = client.get("/api/v1/microsegmentation/network-flow-graph", headers=auth_headers)
        assert mesh_resp.status_code == 200
        assert len(mesh_resp.json()["nodes"]) >= 4
