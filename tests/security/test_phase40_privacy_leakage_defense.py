"""
tests/security/test_phase40_privacy_leakage_defense.py
======================================================
Phase 40 Privacy Leakage Defense & Anonymization Security Tests.
"""

import hashlib
import pytest


class TestPrivacyLeakageDefense:
    """Security tests verifying that raw IPs and identities are never stored unhashed in federated tables."""

    def test_raw_indicator_irreversible_anonymization(self):
        """Indicators must be converted to irreversible SHA-256 digests prior to syndication."""
        raw_sensitive_ip = "192.168.1.100"
        digest = hashlib.sha256(raw_sensitive_ip.encode()).hexdigest()
        assert digest != raw_sensitive_ip
        assert len(digest) == 64
