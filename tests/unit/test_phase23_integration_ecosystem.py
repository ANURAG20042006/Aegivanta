"""
tests/unit/test_phase23_integration_ecosystem.py
=================================================
Phase 23 Enterprise Integration Ecosystem Tests.
Validates Connector SDK, Webhook signing, Replay protection, Exponential backoff, Health scoring.
"""

import pytest
import hashlib
import hmac
from backend.app.services.connector_sdk_service import ConnectorSDKService, CONNECTOR_CATALOG
from backend.app.services.webhook_platform_service import WebhookPlatformService


class TestConnectorSDK:
    """Tests for the Connector SDK Service."""

    def test_connector_catalog_is_populated(self):
        """Catalog must contain at least 15 connectors across all types."""
        assert len(CONNECTOR_CATALOG) >= 15

    def test_connector_catalog_covers_all_types(self):
        """Catalog must cover all required integration types."""
        required_types = {"SIEM", "SOAR", "EDR", "IAM", "TICKETING", "MESSAGING", "THREAT_INTEL", "CLOUD"}
        catalog_types = {c["connector_type"] for c in CONNECTOR_CATALOG}
        assert required_types.issubset(catalog_types)

    def test_get_connector_catalog_returns_descriptions(self):
        """Catalog items must each have a non-empty description."""
        catalog = ConnectorSDKService.get_connector_catalog()
        for item in catalog:
            assert "description" in item
            assert len(item["description"]) > 10

    def test_health_score_perfect_no_failures(self):
        """Zero failures, recent delivery → 100.0 health score."""
        from datetime import datetime, timezone
        score = ConnectorSDKService.calculate_health_score(0, datetime.now(timezone.utc))
        assert score == 100.0

    def test_health_score_decreases_with_failures(self):
        """Each consecutive failure decreases health score by 15."""
        from datetime import datetime, timezone
        score_0 = ConnectorSDKService.calculate_health_score(0, datetime.now(timezone.utc))
        score_3 = ConnectorSDKService.calculate_health_score(3, datetime.now(timezone.utc))
        assert score_0 - score_3 == 45.0

    def test_health_score_maximum_failure_penalty_capped(self):
        """Max failure penalty is capped at 60 regardless of failure count."""
        from datetime import datetime, timezone
        score_100_failures = ConnectorSDKService.calculate_health_score(100, datetime.now(timezone.utc))
        score_5_failures = ConnectorSDKService.calculate_health_score(5, datetime.now(timezone.utc))
        # 5 failures = 75 penalty → capped at 60 → score = 40
        assert score_5_failures == 40.0
        # 100 failures → same cap → score = 40
        assert score_100_failures == 40.0

    def test_health_score_floor_is_zero(self):
        """Health score cannot drop below 0."""
        from datetime import datetime, timezone
        score = ConnectorSDKService.calculate_health_score(100, None)
        assert score >= 0.0

    def test_exponential_backoff_grows_with_attempts(self):
        """Backoff delay must increase with attempt count."""
        delay_1 = ConnectorSDKService.compute_exponential_backoff(1, base_seconds=2.0)
        delay_3 = ConnectorSDKService.compute_exponential_backoff(3, base_seconds=2.0)
        assert delay_3 > delay_1

    def test_exponential_backoff_capped_at_one_hour(self):
        """Backoff is capped at 3600 seconds regardless of attempt count."""
        delay = ConnectorSDKService.compute_exponential_backoff(30, base_seconds=2.0)
        assert delay <= 3600.0

    def test_webhook_hmac_signing_deterministic(self):
        """Two calls with same payload+secret produce same HMAC."""
        payload = b'{"event":"alert.fired","severity":"CRITICAL"}'
        sig1 = ConnectorSDKService.sign_webhook_payload(payload, "test-secret")
        sig2 = ConnectorSDKService.sign_webhook_payload(payload, "test-secret")
        assert sig1 == sig2

    def test_webhook_signature_verification_success(self):
        """Valid signature must verify successfully."""
        payload = b'{"event":"incident.created"}'
        secret = "my-hmac-secret-key-2026"
        sig = ConnectorSDKService.sign_webhook_payload(payload, secret)
        assert ConnectorSDKService.verify_webhook_signature(payload, secret, sig) is True

    def test_webhook_signature_tampered_payload_fails(self):
        """Tampered payload must fail signature verification."""
        payload = b'{"event":"incident.created"}'
        secret = "my-hmac-secret-key-2026"
        sig = ConnectorSDKService.sign_webhook_payload(payload, secret)
        tampered = b'{"event":"incident.created","severity":"LOW"}'
        assert ConnectorSDKService.verify_webhook_signature(tampered, secret, sig) is False

    def test_webhook_wrong_secret_fails_verification(self):
        """Wrong secret must fail signature verification."""
        payload = b'{"event":"alert.fired"}'
        sig = ConnectorSDKService.sign_webhook_payload(payload, "secret-A")
        assert ConnectorSDKService.verify_webhook_signature(payload, "secret-B", sig) is False


class TestWebhookPlatform:
    """Tests for the Webhook Platform Service."""

    def test_replay_protection_first_nonce_passes(self):
        """A fresh nonce should NOT be detected as a replay attack."""
        import uuid
        nonce = str(uuid.uuid4())
        # Reset global seen nonces to avoid test interference
        from backend.app.services.webhook_platform_service import _SEEN_NONCES
        _SEEN_NONCES.discard(nonce)
        assert WebhookPlatformService.is_replay_attack(nonce) is False

    def test_replay_protection_duplicate_nonce_blocked(self):
        """The same nonce used twice must be flagged as a replay attack."""
        import uuid
        nonce = str(uuid.uuid4())
        from backend.app.services.webhook_platform_service import _SEEN_NONCES
        _SEEN_NONCES.discard(nonce)
        WebhookPlatformService.is_replay_attack(nonce)  # First use — should pass
        assert WebhookPlatformService.is_replay_attack(nonce) is True  # Second use — replay

    def test_exponential_retry_next_retry_grows(self):
        """Next retry time must be further in the future as attempt count increases."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        retry_1 = WebhookPlatformService.compute_next_retry(1, base_seconds=2.0)
        retry_3 = WebhookPlatformService.compute_next_retry(3, base_seconds=2.0)
        assert (retry_3 - now).total_seconds() > (retry_1 - now).total_seconds()

    def test_signed_delivery_produces_hmac(self):
        """create_signed_delivery must produce a non-empty HMAC signature."""
        import json
        result = WebhookPlatformService.create_signed_delivery(
            connector_id="conn-test-01",
            event_id="evt-alert-001",
            endpoint_url="https://example.com/webhook",
            payload={"event_type": "ALERT_FIRED", "severity": "HIGH"},
            secret="test-secret-2026"
        )
        assert "hmac_signature" in result
        assert len(result["hmac_signature"]) == 64  # SHA-256 hex digest
        assert "replay_nonce" in result
        assert len(result["replay_nonce"]) == 36  # UUID format
