import os
import pytest
from datetime import timedelta
from fastapi.testclient import TestClient

from backend.app.config import settings, validate_production_settings
from backend.app.main import app
from backend.app.security import create_access_token, decode_access_token, hash_password, verify_password
from backend.app.core.exceptions import AuthenticationError, PermissionDeniedError
from backend.app.models.incident import is_valid_state_transition, ALLOWED_STATE_TRANSITIONS


client = TestClient(app)


def test_1_invalid_operating_mode_raises_error(monkeypatch):
    """Test invalid OPERATING_MODE raises RuntimeError at startup validation."""
    monkeypatch.setattr(settings, "OPERATING_MODE", "INVALID_MODE_123")
    with pytest.raises(RuntimeError, match="Invalid OPERATING_MODE"):
        validate_production_settings()


def test_2_production_secret_key_missing_raises_error(monkeypatch):
    """Test missing SECRET_KEY in production environment halts startup."""
    monkeypatch.setattr(settings, "APP_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="Production requires a unique SECRET_KEY"):
        validate_production_settings()


def test_3_production_postgres_password_missing_raises_error(monkeypatch):
    """Test missing POSTGRES_PASSWORD in production environment halts startup."""
    monkeypatch.setattr(settings, "APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "a_valid_32_character_production_secret_key_12345")
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    with pytest.raises(RuntimeError, match="POSTGRES_PASSWORD"):
        validate_production_settings()


def test_4_jwt_token_encoding_decoding():
    """Test JWT creation and decoding with valid secret and claims."""
    token = create_access_token(subject="user_123", role="admin")
    payload = decode_access_token(token)
    assert payload.get("sub") == "user_123"
    assert payload.get("role") == "admin"


def test_5_expired_jwt_token_raises_authentication_error():
    """Test expired JWT token raises AuthenticationError."""
    expired_token = create_access_token(subject="user_123", role="admin", expires_delta=timedelta(seconds=-10))
    with pytest.raises(AuthenticationError):
        decode_access_token(expired_token)


def test_6_invalid_jwt_token_signature_raises_error():
    """Test malformed/tampered JWT token signature fails decoding."""
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalidpayload.invalid signature"
    with pytest.raises(AuthenticationError):
        decode_access_token(invalid_token)


def test_7_public_register_admin_role_forbidden():
    """Test public /auth/register endpoint rejects admin self-registration with 403 Forbidden or 422 Unprocessable Entity."""
    payload = {
        "username": "self_reg_admin",
        "email": "self_admin@sentinelai.io",
        "password": "SecurePassword123!",
        "full_name": "Self Reg Admin",
        "role": "admin"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code in [403, 422]


def test_8_incident_state_machine_transitions():
    """Test incident state machine allows valid transitions and rejects invalid state jumps."""
    assert is_valid_state_transition("DETECTED", "TRIAGED") is True
    assert is_valid_state_transition("TRIAGED", "INVESTIGATING") is True
    assert is_valid_state_transition("INVESTIGATING", "CONTAINED") is True
    assert is_valid_state_transition("CONTAINED", "RESOLVED") is True
    assert is_valid_state_transition("RESOLVED", "CLOSED") is True

    # Invalid state jumps
    assert is_valid_state_transition("DETECTED", "CLOSED") is False
    assert is_valid_state_transition("DETECTED", "CONTAINED") is False


def test_9_health_probe_liveness():
    """Test GET /health returns liveness status and environment telemetry."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "HEALTHY"
    assert data.get("service") == "SentinelAI"
    assert "mode" in data


def test_10_request_correlation_id_middleware():
    """Test X-Request-ID header is present in API responses."""
    response = client.get("/health")
    assert "x-request-id" in response.headers
    assert len(response.headers["x-request-id"]) > 0
