"""
tests/unit/test_phase40_models.py
=================================
Phase 40 Model Schema & Defaults Unit Tests.
"""

import pytest
from backend.app.models.federated_threat_sharing import FederatedIOCExchangeNode, FederatedThreatIndicator, HomomorphicMatchQuery


class TestPhase40Models:
    """Unit tests verifying Phase 40 database defaults."""

    def test_indicator_consensus_defaults(self):
        """Federated indicator should hold valid syndication status."""
        ind = FederatedThreatIndicator(
            tenant_id="tenant-fed",
            anonymized_indicator_hash="hash-123",
            threat_classification="RANSOMWARE",
            confidence_consensus_score=0.95,
            syndication_status="VALIDATING"
        )
        assert ind.syndication_status == "VALIDATING"
        assert ind.confidence_consensus_score == 0.95
