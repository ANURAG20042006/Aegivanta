"""
tests/integration/test_phase3_7_response_api.py
===============================================
Phase 3.7 Integration Tests: Autonomous Incident Response + SOAR REST APIs.
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def get_auth_headers(role: str = "admin") -> dict:
    env_map = {
        "admin": "SENTINEL_ADMIN_PASSWORD",
        "analyst": "SENTINEL_ANALYST_PASSWORD",
        "viewer": "SENTINEL_VIEWER_PASSWORD"
    }
    password = os.getenv(env_map.get(role, "SENTINEL_ADMIN_PASSWORD"), "TestAdminPassword2026!")
    res = client.post("/api/v1/auth/login", data={"username": role, "password": password})
    assert res.status_code == 200, f"Login failed for {role}: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
def test_full_incident_to_response_and_rollback_flow():
    """Verify end-to-end flow: correlate incident -> evaluate -> preview -> submit -> approve -> verify -> rollback -> audit."""
    admin_hdr = get_auth_headers("admin")
    analyst_hdr = get_auth_headers("analyst")

    # 1. Create Incident via correlation
    corr_payload = {
        "events": [
            {
                "id": "soar-int-ev-01",
                "source_ip": "198.51.100.77",
                "destination_ip": "10.0.0.10",
                "destination_port": 445,
                "is_malicious": True,
                "attack_type": "Brute Force",
                "auth_failures": 9,
                "timestamp": "2026-08-20T10:00:00Z"
            }
        ]
    }
    res_corr = client.post("/api/v1/incidents/correlate", json=corr_payload, headers=admin_hdr)
    assert res_corr.status_code == 200
    inc_id = res_corr.json()["incidents"][0]["incident_id"]

    # 2. Evaluate Strategy
    res_eval = client.post(
        "/api/v1/response/evaluate",
        json={
            "incident_id": inc_id,
            "risk_score": 85.0,
            "severity": "CRITICAL",
            "attack_type": "Brute Force",
            "source_ip": "198.51.100.77"
        },
        headers=analyst_hdr
    )
    assert res_eval.status_code == 200
    eval_data = res_eval.json()
    assert eval_data["primary_recommended_action"] in ["BLOCK_IP", "ISOLATE_HOST"]

    # 3. Preview Action
    res_prev = client.post(
        "/api/v1/response/actions/preview",
        json={"incident_id": inc_id, "action_type": "BLOCK_IP", "target_entity": "198.51.100.77"},
        headers=analyst_hdr
    )
    assert res_prev.status_code == 200
    assert res_prev.json()["would_execute"] is True

    # 4. Submit Action Request (Dry-Run = False)
    submit_headers = dict(analyst_hdr)
    submit_headers["X-Idempotency-Key"] = "soar-idem-test-01"
    res_sub = client.post(
        "/api/v1/response/actions",
        json={"incident_id": inc_id, "action_type": "BLOCK_IP", "target_entity": "198.51.100.77", "is_dry_run": False},
        headers=submit_headers
    )
    assert res_sub.status_code == 201
    act_data = res_sub.json()
    act_id = act_data["id"]
    status_curr = act_data["status"]

    # 5. If PENDING_APPROVAL, approve it via Admin
    if status_curr == "PENDING_APPROVAL":
        res_app = client.post(f"/api/v1/response/actions/{act_id}/approve", headers=admin_hdr)
        assert res_app.status_code == 200
        assert res_app.json()["current_status"] in ["EXECUTING", "VERIFYING", "SUCCEEDED"]

    # 6. Fetch Action Details & Verification
    res_act = client.get(f"/api/v1/response/actions/{act_id}", headers=analyst_hdr)
    assert res_act.status_code == 200
    assert res_act.json()["status"] == "SUCCEEDED"
    assert res_act.json()["verification_result"]["verified"] is True

    # 7. Check Audit Log
    res_audit = client.get(f"/api/v1/response/actions/{act_id}/audit", headers=analyst_hdr)
    assert res_audit.status_code == 200
    assert len(res_audit.json()) >= 1

    # 8. Rollback Action
    res_rb = client.post(f"/api/v1/response/actions/{act_id}/rollback", headers=admin_hdr)
    assert res_rb.status_code == 200
    assert res_rb.json()["status"] == "ROLLED_BACK"

    # 9. Verify Action Record reflects ROLLED_BACK
    res_final = client.get(f"/api/v1/response/actions/{act_id}", headers=analyst_hdr)
    assert res_final.json()["status"] == "ROLLED_BACK"
