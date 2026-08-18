"""
tests/security/test_security_audit_fixes.py
============================================
Verification test suite for all Security Audit fixes:
1. WebSocket DB-backed JWT authentication and role authorization
2. WebSocket rejection of deactivated/deleted users
3. Login dual-bucket rate limiting (per-IP and per-IP:username)
4. Register rate limiting
5. Playbook simulation status integrity (SIMULATED_EXECUTION)
6. Response orchestrator role normalization
7. Input schema fail-closed enforcement for single & CSV prediction
8. Concurrent training job locking (HTTP 409 Conflict)
9. Production CORS configuration safety
"""

import pytest
import os
import uuid
from fastapi.testclient import TestClient
from fastapi import HTTPException
from starlette.websockets import WebSocketDisconnect

from backend.app.main import app
from backend.app.security import create_access_token
from backend.app.core.rate_limit import LoginRateLimiter, RateLimiter
from backend.app.services.playbook_service import PlaybookService
from backend.app.services.response_orchestrator import ResponseOrchestrator
from backend.app.services.predict_service import predict_service
from backend.app.models.response_approval import ResponseApproval
from backend.app.models.user import User
from backend.app.models.training_job import TrainingJob
from backend.app.database import AsyncSessionFactory
from backend.app.config import Settings, validate_production_settings


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


@pytest.mark.asyncio
async def test_websocket_deactivated_user_rejected():
    """WebSocket connection for a deactivated/deleted user in DB must be rejected."""
    deact_username = f"deact_{uuid.uuid4().hex[:6]}"
    async with AsyncSessionFactory() as db:
        user = User(
            username=deact_username,
            email=f"{deact_username}@example.com",
            password_hash="test_hashed_password_string_here",
            full_name="Deactivated Analyst",
            role="analyst",
            is_active=False
        )
        db.add(user)
        await db.commit()

    token = create_access_token(subject=deact_username, role="analyst")
    with pytest.raises(Exception):
        with client.websocket_connect(f"/ws/threats?token={token}") as ws:
            ws.receive_json()


def test_websocket_authenticated_connected():
    """WebSocket connection with valid active user JWT connects and receives telemetry."""
    valid_token = create_access_token(subject="admin", role="admin")
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


@pytest.mark.asyncio
async def test_invalid_prediction_input_raises_400():
    """PredictService rejects invalid non-dictionary/non-vector inputs with HTTP 400."""
    async with AsyncSessionFactory() as db:
        with pytest.raises(HTTPException) as exc:
            await predict_service.predict_single_flow(db, features="invalid_string_not_dict")
        assert exc.value.status_code == 400
        assert "Invalid feature payload" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_empty_csv_raises_400():
    """PredictService rejects empty CSV uploads with HTTP 400."""
    async with AsyncSessionFactory() as db:
        with pytest.raises(HTTPException) as exc:
            await predict_service.predict_csv_batch(db, file_content=b"")
        assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_concurrent_training_jobs_rejected():
    """Training trigger endpoint rejects concurrent jobs with HTTP 409 Conflict."""
    async with AsyncSessionFactory() as db:
        # Create an active job in QUEUED status
        job = TrainingJob(status="QUEUED", model_name="CatBoost")
        db.add(job)
        await db.commit()

        try:
            admin_user = User(username="admin_test", role="admin", is_active=True)

            from backend.app.api.v1.train import trigger_training_pipeline
            from fastapi import BackgroundTasks
            bg = BackgroundTasks()

            with pytest.raises(HTTPException) as exc:
                await trigger_training_pipeline(background_tasks=bg, db=db, admin_user=admin_user)

            assert exc.value.status_code == 409
            assert "Concurrent training execution is disallowed" in str(exc.value.detail)
        finally:
            await db.delete(job)
            await db.commit()


def test_production_cors_validation_safety():
    """Production configuration validator enforces safe non-localhost CORS origins."""
    # Safe production settings
    safe_settings = Settings(
        APP_ENV="production",
        OPERATING_MODE="PRODUCTION",
        SECRET_KEY="high_entropy_unique_production_secret_key_32_chars!",
        POSTGRES_PASSWORD="secure_password_123",
        CORS_ORIGINS=["https://sentinelai.io", "https://app.sentinelai.io"]
    )
    validate_production_settings(safe_settings)

    # Insecure localhost settings must fail
    insecure_settings = Settings(
        APP_ENV="production",
        OPERATING_MODE="PRODUCTION",
        SECRET_KEY="high_entropy_unique_production_secret_key_32_chars!",
        POSTGRES_PASSWORD="secure_password_123",
        CORS_ORIGINS=["http://localhost:5173"]
    )
    with pytest.raises(RuntimeError, match="Production CORS_ORIGINS"):
        validate_production_settings(insecure_settings)
