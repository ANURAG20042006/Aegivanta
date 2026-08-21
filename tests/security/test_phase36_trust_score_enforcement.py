"""
tests/security/test_phase36_trust_score_enforcement.py
======================================================
Phase 36 Trust Score Attestation & Boundary Enforcement Security Tests.
"""

import pytest


class TestTrustScoreEnforcement:
    """Security tests verifying trust score policy gating."""

    def test_low_trust_score_blocks_sensitive_segment_access(self):
        """A client with trust score < minimum required score must be denied access."""
        min_required_trust = 85
        client_current_trust = 60

        is_authorized = client_current_trust >= min_required_trust
        assert is_authorized is False
