"""
tests/unit/test_phase40_differential_privacy.py
===============================================
Phase 40 Differential Privacy Noise Unit Tests.
"""

import pytest
from backend.app.models.federated_threat_sharing import FederatedThreatIndicator
from backend.app.services.differential_privacy_service import DifferentialPrivacyService


class TestDifferentialPrivacy:
    """Unit tests for FederatedThreatIndicator and noise injection."""

    def test_federated_indicator_model(self):
        """FederatedThreatIndicator must store anonymized hash, classification, epsilon, and consensus."""
        ind = FederatedThreatIndicator(
            tenant_id="tenant-fed",
            anonymized_indicator_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            threat_classification="APT_C2_INFRASTRUCTURE",
            differential_privacy_epsilon=0.5,
            confidence_consensus_score=0.98,
            peer_validations_count=16,
            syndication_status="CONSENSUS_REACHED"
        )
        assert len(ind.anonymized_indicator_hash) == 64
        assert ind.differential_privacy_epsilon == 0.5
        assert ind.syndication_status == "CONSENSUS_REACHED"

    def test_laplace_noise_injection_non_negative(self):
        """Laplace noise injection on sighting counts must return non-negative integer."""
        noisy_count = DifferentialPrivacyService.apply_laplace_noise(10, epsilon=0.5)
        assert isinstance(noisy_count, int)
        assert noisy_count >= 0
