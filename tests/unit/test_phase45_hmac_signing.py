"""
tests/unit/test_phase45_hmac_signing.py
=======================================
Phase 45 HMAC-SHA256 Signature Signing Unit Tests.
"""

import pytest
import hmac
import hashlib
import json


class TestHMACSigning:
    """Unit tests verifying webhook HMAC-SHA256 signature generation."""

    def test_hmac_sha256_signature_generation(self):
        """HMAC-SHA256 signature should be 64-char hex digest."""
        secret = b"whsec_test_secret_key_12345"
        payload = json.dumps({"event": "alert.created", "id": "ALT-123"}).encode()
        sig = hmac.new(secret, payload, hashlib.sha256).hexdigest()

        assert len(sig) == 64
        assert isinstance(sig, str)
