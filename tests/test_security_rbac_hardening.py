"""
tests/test_security_rbac_hardening.py
======================================
Comprehensive Security, Secret Management, Health Probes & RBAC Hardening Test Suite.
"""

import os
import uuid
import pytest
from datetime import timedelta
from fastapi.testclient import TestClient

from backend.app.config import Settings, settings, validate_production_settings
from backend.app.main import app
from backend.app.security import create_access_token, decode_access_token, hash_password, verify_password
from backend.app.core.dependencies import normalize_role, require_role
from backend.app.core.exceptions import AuthenticationError, PermissionDeniedError
from backend.app.models.incident import is_valid_state_transition


client = TestClient(app)


def get_auth_token(role: str = "admin") -> dict:
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


# ==============================================================================
# ISSUE 1: SECRET MANAGEMENT TESTS
# ==============================================================================

def test_production_missing_secret_key_fails(monkeypatch):
    """Test missing SECRET_KEY in production halts startup."""
    monkeypatch.delenv("SECRET_KEY", raising=False)
    prod_settings = Settings(
        APP_ENV="production",
        OPERATING_MODE="PRODUCTION",
        SECRET_KEY="",
        POSTGRES_PASSWORD="SuperSecretPassword123!"
    )
    with pytest.raises(RuntimeError, match="SECRET_KEY of at least 32 characters"):
        validate_production_settings(prod_settings)


def test_production_weak_secret_key_fails(monkeypatch):
    """Test weak or predictable SECRET_KEY in production halts startup."""
    monkeypatch.setenv("SECRET_KEY", "changeme")
    prod_settings = Settings(
        APP_ENV="production",
        OPERATING_MODE="PRODUCTION",
        SECRET_KEY="changeme",
        POSTGRES_PASSWORD="SuperSecretPassword123!"
    )
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        validate_production_settings(prod_settings)


def test_production_missing_postgres_password_fails(monkeypatch):
    """Test missing POSTGRES_PASSWORD in production halts startup."""
    monkeypatch.setenv("SECRET_KEY", "a_very_strong_and_secure_production_secret_key_32_bytes_long!")
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    prod_settings = Settings(
        APP_ENV="production",
        OPERATING_MODE="PRODUCTION",
        SECRET_KEY="a_very_strong_and_secure_production_secret_key_32_bytes_long!",
        POSTGRES_PASSWORD=""
    )
    with pytest.raises(RuntimeError, match="POSTGRES_PASSWORD"):
        validate_production_settings(prod_settings)


def test_production_valid_configuration_passes(monkeypatch):
    """Test complete and valid production configuration passes validation."""
    monkeypatch.setenv("SECRET_KEY", "a_very_strong_and_secure_production_secret_key_32_bytes_long!")
    monkeypatch.setenv("POSTGRES_PASSWORD", "SuperSecurePostgresPass2026!")
    monkeypatch.setenv("SENTINEL_ADMIN_PASSWORD", "AdminSecurePass2026!")
    monkeypatch.setenv("SENTINEL_ANALYST_PASSWORD", "AnalystSecurePass2026!")
    monkeypatch.setenv("SENTINEL_VIEWER_PASSWORD", "ViewerSecurePass2026!")

    prod_settings = Settings(
        APP_ENV="production",
        OPERATING_MODE="PRODUCTION",
        DEBUG=False,
        DATABASE_URL="postgresql+asyncpg://postgres:SuperSecurePostgresPass2026!@localhost:5432/aegivanta_prod",
        CORS_ORIGINS=["https://soc.sentinelai.internal"]
    )
    # Should complete with zero errors
    validate_production_settings(prod_settings)



def test_development_test_configuration_passes(monkeypatch):
    """Test development mode allows development settings without crashing."""
    dev_settings = Settings(
        APP_ENV="development",
        OPERATING_MODE="DEMO",
        DEBUG=False
    )
    validate_production_settings(dev_settings)


# ==============================================================================
# ISSUE 2 & 5: AUTHORIZATION, RBAC & ROLE ALIASES TESTS
# ==============================================================================

def test_canonical_role_normalization():
    """Test role normalization maps aliases to canonical representations and fails closed on unknown roles."""
    assert normalize_role("admin") == "admin"
    assert normalize_role("ADMIN") == "admin"
    assert normalize_role("administrator") == "admin"
    assert normalize_role("root") == "admin"

    assert normalize_role("analyst") == "analyst"
    assert normalize_role("Soc_Analyst") == "analyst"
    assert normalize_role("security_analyst") == "analyst"

    assert normalize_role("viewer") == "viewer"
    assert normalize_role("read_only") == "viewer"
    assert normalize_role("guest") == "viewer"
    assert normalize_role("auditor") == "viewer"

    # Unknown / unmapped roles must fail closed to 'unknown'
    assert normalize_role("superuser") == "unknown"
    assert normalize_role("hacker") == "unknown"
    assert normalize_role("operator") == "unknown"
    assert normalize_role("") == "unknown"
    assert normalize_role(None) == "unknown"


def test_public_registration_blocks_privileged_roles():
    """Test /auth/register prevents self-granting Admin or Analyst roles."""
    admin_payload = {
        "username": f"bad_admin_{uuid.uuid4().hex[:4]}",
        "email": f"bad_admin_{uuid.uuid4().hex[:4]}@sentinelai.io",
        "password": "SecurePassword123!",
        "full_name": "Privilege Escalation Attempt",
        "role": "admin"
    }
    res_admin = client.post("/api/v1/auth/register", json=admin_payload)
    assert res_admin.status_code in [403, 422]

    analyst_payload = {
        "username": f"bad_analyst_{uuid.uuid4().hex[:4]}",
        "email": f"bad_analyst_{uuid.uuid4().hex[:4]}@sentinelai.io",
        "password": "SecurePassword123!",
        "full_name": "Analyst Escalation Attempt",
        "role": "analyst"
    }
    res_analyst = client.post("/api/v1/auth/register", json=analyst_payload)
    assert res_analyst.status_code in [403, 422]


def test_viewer_role_authorization_boundaries():
    """Verify that Viewer cannot create assets, update alerts, or remediate incidents."""
    viewer_hdr = get_auth_token("viewer")

    # 1. Viewer cannot create protected asset (403)
    res_asset = client.post("/api/v1/assets", json={
        "name": "Unauthorized Asset",
        "hostname": "unauth.internal",
        "ip_address": "10.0.0.99",
        "asset_type": "server",
        "environment": "production",
        "criticality": "high"
    }, headers=viewer_hdr)
    assert res_asset.status_code == 403

    # 2. Viewer cannot update alert status (403)
    res_alert = client.patch("/api/v1/alerts/non_existent_id/status", json={"status": "resolved"}, headers=viewer_hdr)
    assert res_alert.status_code == 403

    # 3. Viewer cannot update incident status (403)
    res_inc = client.patch("/api/v1/incidents/non_existent_id/status", json={"status": "INVESTIGATING"}, headers=viewer_hdr)
    assert res_inc.status_code == 403

    # 4. Viewer cannot execute threat remediation (403)
    res_rem = client.post("/api/v1/incidents/non_existent_id/remediate", json={"action": "BLOCK_IP"}, headers=viewer_hdr)
    assert res_rem.status_code == 403


# ==============================================================================
# ISSUE 3 & 6: HEALTH PROBES, LIVENESS, READINESS & ZERO SECRET LEAKAGE
# ==============================================================================

def test_liveness_probes():
    """Test /health and /health/live return healthy status without heavy operations."""
    res1 = client.get("/health")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1.get("status") == "HEALTHY"
    assert data1.get("service") == settings.APP_NAME

    res2 = client.get("/health/live")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2.get("status") == "HEALTHY"


def test_readiness_probe_success():
    """Test /ready and /health/ready return 200 OK when database and artifacts are healthy."""
    res = client.get("/ready")
    assert res.status_code == 200
    data = res.json()
    assert data.get("ready") is True
    assert data.get("database_connected") is True
    assert data.get("artifact_integrity") is True

    res2 = client.get("/health/ready")
    assert res2.status_code == 200


def test_health_endpoints_do_not_leak_secrets():
    """Test health and metrics endpoints never expose passwords, connection strings, or secret keys."""
    endpoints = ["/health", "/health/live", "/ready", "/health/ready", "/metrics"]
    forbidden_tokens = ["password", "secret_key", "bearer", "postgres://", "sqlite://", "redis://", "authorization"]

    for ep in endpoints:
        res = client.get(ep)
        text_lower = res.text.lower()
        for token in forbidden_tokens:
            assert token not in text_lower, f"Sensitive token '{token}' leaked in endpoint '{ep}' response: {res.text}"


def test_metrics_endpoint_runtime_values():
    """Test /metrics returns measured database latency and runtime metadata."""
    res = client.get("/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "database_latency_ms" in data
    assert "uptime_seconds" in data
    assert data.get("database_healthy") is True
    assert data.get("telemetry_source") == "RUNTIME_MEASURED"


# ==============================================================================
# ISSUE 4: REQUEST ID & TRACEABILITY TESTS
# ==============================================================================

def test_request_id_generated_when_missing():
    """Test X-Request-ID is generated and returned when not supplied by client."""
    res = client.get("/health")
    assert "x-request-id" in res.headers
    req_id = res.headers["x-request-id"]
    assert len(req_id) >= 16


def test_request_id_preserved_when_valid():
    """Test valid client-supplied X-Request-ID is preserved and echoed back."""
    custom_id = "soc-trace-req-998877"
    res = client.get("/health", headers={"X-Request-ID": custom_id})
    assert res.headers.get("x-request-id") == custom_id


def test_request_id_sanitized_when_malformed():
    """Test malicious/malformed X-Request-ID is replaced with a safe UUID."""
    malicious_id = "attack-id'; DROP TABLE users; --"
    res = client.get("/health", headers={"X-Request-ID": malicious_id})
    returned_id = res.headers.get("x-request-id")
    assert returned_id != malicious_id
    assert ";" not in returned_id
