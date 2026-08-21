"""
tests/unit/test_phase40_homomorphic_match.py
============================================
Phase 40 Homomorphic Encrypted Blind Match Unit Tests.
"""

import pytest
from backend.app.models.federated_threat_sharing import HomomorphicMatchQuery


class TestHomomorphicMatch:
    """Unit tests for HomomorphicMatchQuery model."""

    def test_blind_match_query_model(self):
        """HomomorphicMatchQuery must store query hash, status, and latency."""
        qry = HomomorphicMatchQuery(
            tenant_id="tenant-fed",
            encrypted_query_hash="abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
            blind_match_status="BLIND_MATCH_FOUND",
            execution_time_ms=1.92
        )
        assert qry.blind_match_status == "BLIND_MATCH_FOUND"
        assert qry.execution_time_ms == 1.92
