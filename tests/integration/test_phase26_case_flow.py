"""
tests/integration/test_phase26_case_flow.py
===========================================
Phase 26 SOC Case Management & Forensic Evidence Flow Tests.
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


class TestSOCCaseFlow:
    """Integration flow for SOC case creation, lifecycle transitions, and evidence verification."""

    def test_case_lifecycle_and_evidence_flow(self, client, auth_headers):
        """Tests case creation, status transition, task/comment addition, and evidence attachment."""
        # 1. Create Case
        create_resp = client.post(
            "/api/v1/soc/cases",
            json={
                "title": "Integration Test Case: Lateral SMB",
                "description": "Test case for multi-hop lateral movement verification.",
                "priority": "HIGH",
                "severity": "HIGH",
                "affected_assets": ["HOST-TEST-01"],
                "affected_identities": ["bob.test"]
            },
            headers=auth_headers
        )
        assert create_resp.status_code == 200
        case_data = create_resp.json()
        case_id = case_data["id"]
        assert case_data["status"] == "OPEN"

        # 2. Update Status to INVESTIGATING
        status_resp = client.put(
            f"/api/v1/soc/cases/{case_id}/status",
            json={"status": "INVESTIGATING"},
            headers=auth_headers
        )
        assert status_resp.status_code == 200
        assert status_resp.json()["new_status"] == "INVESTIGATING"

        # 3. Add Task
        task_resp = client.post(
            f"/api/v1/soc/cases/{case_id}/tasks",
            json={"title": "Verify endpoint memory image"},
            headers=auth_headers
        )
        assert task_resp.status_code == 200
        assert task_resp.json()["status"] == "PENDING"

        # 4. Attach Forensic Evidence
        ev_resp = client.post(
            f"/api/v1/soc/cases/{case_id}/evidence",
            json={
                "title": "Evidence Item: PowerShell Event",
                "description": "Recorded process execution log",
                "evidence_type": "PROCESS_EVENT",
                "raw_payload": {"cmd": "powershell.exe -enc"},
                "source_system": "aegivanta.edr"
            },
            headers=auth_headers
        )
        assert ev_resp.status_code == 200
        ev_data = ev_resp.json()
        ev_id = ev_data["id"]
        assert len(ev_data["sha256_hash"]) == 64
        assert ev_data["integrity_verified"] is True

        # 5. Verify Evidence Cryptographic Integrity
        verify_resp = client.get(f"/api/v1/soc/evidence/{ev_id}/verify", headers=auth_headers)
        assert verify_resp.status_code == 200
        assert verify_resp.json()["integrity_verified"] is True
