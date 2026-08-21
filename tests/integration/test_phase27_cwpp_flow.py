"""
tests/integration/test_phase27_cwpp_flow.py
===========================================
Phase 27 CWPP Workload Threat Defense Integration Flow Tests.
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


class TestCWPPIntegrationFlow:
    """Integration tests for CWPP runtime threat detections and containment."""

    def test_cwpp_findings_and_simulation_flow(self, client, auth_headers):
        """Lists findings, simulates threat, and quarantines workload."""
        # 1. List findings
        list_resp = client.get("/api/v1/cloud-security/cwpp/findings", headers=auth_headers)
        assert list_resp.status_code == 200
        findings = list_resp.json()
        assert len(findings) >= 1

        # 2. Simulate threat
        sim_resp = client.post(
            "/api/v1/cloud-security/cwpp/simulate-threat",
            json={
                "workload_type": "K8S_POD",
                "threat_type": "REVERSE_SHELL",
                "target_name": "test-pod-cwpp"
            },
            headers=auth_headers
        )
        assert sim_resp.status_code == 200
        f_id = sim_resp.json()["finding_id"]

        # 3. Contain workload
        contain_resp = client.post(f"/api/v1/cloud-security/cwpp/contain/{f_id}", headers=auth_headers)
        assert contain_resp.status_code == 200
        assert contain_resp.json()["containment_status"] == "CONTAINED"

    def test_serverless_and_k8s_clusters_flow(self, client, auth_headers):
        """Audits serverless and registers K8s clusters."""
        # Serverless findings
        srv_resp = client.get("/api/v1/cloud-security/serverless/findings", headers=auth_headers)
        assert srv_resp.status_code == 200
        assert len(srv_resp.json()) >= 1

        # K8s clusters
        cls_resp = client.get("/api/v1/cloud-security/k8s/clusters", headers=auth_headers)
        assert cls_resp.status_code == 200
        assert len(cls_resp.json()) >= 1
