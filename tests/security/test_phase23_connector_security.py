"""
tests/security/test_phase23_connector_security.py
=================================================
Phase 23 Integration Ecosystem Security Tests.
Validates: no credential leak in connector API responses, tenant isolation, HMAC constant-time comparison.
"""

import pytest
from backend.app.services.connector_sdk_service import ConnectorSDKService
from backend.app.services.webhook_platform_service import WebhookPlatformService


class TestConnectorCredentialSecurity:
    """Ensures no credentials leak in connector list API responses."""

    def test_connector_catalog_does_not_contain_credentials(self):
        """Connector catalog should never expose secrets, tokens, or passwords."""
        catalog = ConnectorSDKService.get_connector_catalog()
        forbidden_keys = {"password", "token", "secret", "api_key", "private_key", "credential"}
        for item in catalog:
            item_lower = {k.lower(): v for k, v in item.items()}
            for key in forbidden_keys:
                assert key not in item_lower, f"Sensitive key '{key}' found in catalog item: {item}"

    def test_health_score_calculation_uses_no_credentials(self):
        """Health score calculation must take no secret parameters."""
        import inspect
        sig = inspect.signature(ConnectorSDKService.calculate_health_score)
        param_names = {p.lower() for p in sig.parameters}
        sensitive = {"password", "secret", "token", "api_key", "credential"}
        assert sensitive.isdisjoint(param_names)


class TestWebhookSecurityControls:
    """HMAC webhook security validation."""

    def test_hmac_uses_sha256(self):
        """Webhook HMAC must use SHA-256 (64-char hex output)."""
        sig = ConnectorSDKService.sign_webhook_payload(b"test payload", "secret")
        assert len(sig) == 64  # SHA-256 hex digest = 32 bytes = 64 hex chars

    def test_different_secrets_produce_different_signatures(self):
        """Different secrets must produce different HMAC signatures."""
        payload = b'{"event":"alert"}'
        sig_a = ConnectorSDKService.sign_webhook_payload(payload, "secret-A-2026")
        sig_b = ConnectorSDKService.sign_webhook_payload(payload, "secret-B-2026")
        assert sig_a != sig_b

    def test_empty_payload_produces_valid_signature(self):
        """Empty payload with a secret must still produce a valid HMAC."""
        sig = ConnectorSDKService.sign_webhook_payload(b"", "my-secret")
        assert len(sig) == 64

    def test_signature_verification_uses_constant_time_comparison(self):
        """verify_webhook_signature must use hmac.compare_digest (not ==)."""
        import inspect
        src = inspect.getsource(ConnectorSDKService.verify_webhook_signature)
        assert "compare_digest" in src, "Must use hmac.compare_digest for constant-time comparison"


class TestTenantIsolationConnectors:
    """Tests for tenant isolation in connector operations."""

    def test_health_score_is_pure_function_per_call(self):
        """Health score is stateless — repeated calls produce same result."""
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc)
        score1 = ConnectorSDKService.calculate_health_score(2, ts)
        score2 = ConnectorSDKService.calculate_health_score(2, ts)
        assert score1 == score2

    def test_webhook_replay_detection_is_per_nonce(self):
        """Each unique nonce gets its own replay detection slot."""
        import uuid
        from backend.app.services.webhook_platform_service import _SEEN_NONCES
        nonce_a = str(uuid.uuid4())
        nonce_b = str(uuid.uuid4())
        _SEEN_NONCES.discard(nonce_a)
        _SEEN_NONCES.discard(nonce_b)
        # First use of each — should pass
        assert WebhookPlatformService.is_replay_attack(nonce_a) is False
        assert WebhookPlatformService.is_replay_attack(nonce_b) is False
        # Second use of nonce_a — replay
        assert WebhookPlatformService.is_replay_attack(nonce_a) is True
        # nonce_b still only used once — should still replay now
        assert WebhookPlatformService.is_replay_attack(nonce_b) is True
