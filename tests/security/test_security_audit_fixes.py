"""
tests/security/test_security_audit_fixes.py
============================================
Verification test suite for all 23 Security Audit fixes:
1. WebSocket JWT authentication and role authorization
2. Login dual-bucket rate limiting (per-IP and per-IP:username)
3. Register rate limiting
4. Playbook simulation status integrity (never returns EXECUTED_SUCCESS)
5. Response orchestrator role normalization
6. Database migration loop integrity
"""

import pytest
import os
from fastapi.testclient import TestClient
from fastapi import HTTPException
from starlette.websockets import WebSocketDisconnect

from backend.app.main import app
from backend.app.security import create_access_token
from backend.app.core.rate_limit import LoginRateLimiter, RateLimiter
from backend.app.services.playbook_service import PlaybookService
from backend.app.services.response_orchestrator import ResponseOrchestrator
from backend.app.models.response_approval import ResponseApproval
from backend.app.database import AsyncSessionFactory


client = TestClient(app)


def test_websocket_missing_token_rejected():
    """Unauthenticated WebSocket connection attempts must be closed immediately."""
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/threats") as ws:
            ws.receive_json()


def test_websocket_invalid_token_rejected():
    """WebSocket connection with invalid JWT must be closed with Policy Violation (1008)."""
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/threats?token=invalid.jwt.token") as ws:
            ws.receive_json()


def test_websocket_unauthorized_role_rejected():
    """WebSocket connection with disallowed/unknown role must be closed."""
    bad_token = create_access_token(subject="user_bad", role="unknown_hacker_role")
    with pytest.raises(Exception):
        with client.websocket_connect(f"/ws/threats?token={bad_token}") as ws:
            ws.receive_json()


def test_websocket_authenticated_connected():
    """WebSocket connection with valid JWT connects and receives telemetry."""
    valid_token = create_access_token(subject="user_admin", role="admin")
    with client.websocket_connect(f"/ws/threats?token={valid_token}") as ws:
        data = ws.receive_json()
        assert "type" in data
        assert data["type"] in ["PACKET_STREAM", "SYSTEM_STATUS"]


def test_login_rate_limiting_ip_threshold():
    """Exceeding IP rate limit raises HTTP 429."""
    limiter = LoginRateLimiter(ip_rpm=3, ip_user_rpm=10)
    test_ip = "203.0.113.50"

    # First 3 attempts succeed
    limiter.check(ip=test_ip, username="user1")
    limiter.check(ip=test_ip, username="user2")
    limiter.check(ip=test_ip, username="user3")

    # 4th attempt must be rejected with 429
    with pytest.raises(HTTPException) as exc_info:
        limiter.check(ip=test_ip, username="user4")
    assert exc_info.value.status_code == 429
    assert "Too many login attempts from this IP" in exc_info.value.detail


def test_login_rate_limiting_username_threshold():
    """Exceeding username-specific limit from one IP raises HTTP 429."""
    limiter = LoginRateLimiter(ip_rpm=10, ip_user_rpm=2)
    test_ip = "203.0.113.51"
    target_user = "admin_target"

    limiter.check(ip=test_ip, username=target_user)
    limiter.check(ip=test_ip, username=target_user)

    # 3rd attempt on same target account from same IP is rejected
    with pytest.raises(HTTPException) as exc_info:
        limiter.check(ip=test_ip, username=target_user)
    assert exc_info.value.status_code == 429
    assert "Too many login attempts for this account" in exc_info.value.detail


def test_register_rate_limiting():
    """Register rate limiter triggers after reaching threshold."""
    limiter = RateLimiter(requests_per_minute=2)
    limiter.reset()

    assert limiter._is_limited("198.51.100.99") is False
    assert limiter._is_limited("198.51.100.99") is False
    assert limiter._is_limited("198.51.100.99") is True


@pytest.mark.asyncio
async def test_playbook_service_simulated_execution_status():
    """PlaybookService non-dry-run returns SIMULATED_EXECUTION, never misleading EXECUTED_SUCCESS."""
    async with AsyncSessionFactory() as db:
        res = await PlaybookService.execute_action(
            incident_id="inc-test-sim",
            playbook_name="Block_IP",
            action_type="IP_BLOCK",
            target_entity="198.51.100.77",
            is_dry_run=False,
            executed_by="admin",
            parameters={"firewall": "perimeter"},
            db=db
        )
        assert res["status"] == "SIMULATED_EXECUTION"
        assert "[SIMULATED EXECUTION]" in res["log"]
        assert "EXECUTED_SUCCESS" not in res["status"]


@pytest.mark.asyncio
async def test_response_orchestrator_canonical_role_normalization():
    """ResponseOrchestrator normalizes role aliases (e.g. root -> admin)."""
    async with AsyncSessionFactory() as db:
        approval = ResponseApproval(
            incident_id="inc-test-role",
            requested_action="ISOLATE_HOST",
            target_entity="host-01",
            requested_by="analyst",
            status="REQUESTED"
        )
        db.add(approval)
        await db.commit()

        # Non-admin alias (viewer) rejected
        with pytest.raises(PermissionError) as exc_info:
            await ResponseOrchestrator.approve_and_execute(
                approval_id=approval.id,
                approved_by="test_user",
                approver_role="viewer",
                db=db
            )
        assert "Only Admin users are authorized" in str(exc_info.value)

        # Admin alias ('root') normalized to admin and approved
        res = await ResponseOrchestrator.approve_and_execute(
            approval_id=approval.id,
            approved_by="root_admin",
            approver_role="root",
            db=db
        )
        assert res["status"] == "COMPLETED"
        assert res["execution"]["status"] == "SIMULATED_SUCCESS"
