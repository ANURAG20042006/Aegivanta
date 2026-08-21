"""
tests/unit/test_phase40_federated_exchange.py
=============================================
Phase 40 Federated Exchange Node Unit Tests.
"""

import pytest
from backend.app.models.federated_threat_sharing import FederatedIOCExchangeNode


class TestFederatedExchange:
    """Unit tests for FederatedIOCExchangeNode model."""

    def test_exchange_node_model_creation(self):
        """FederatedIOCExchangeNode must store pseudonym, trust tier, weight, and key hash."""
        node = FederatedIOCExchangeNode(
            tenant_id="tenant-fed",
            node_pseudonym="US-EAST-ALLIANCE-01",
            trust_tier="GOV_CERT",
            consensus_weight=1.5,
            public_key_hash="abcdef0123456789abcdef0123456789",
            status="ACTIVE"
        )
        assert node.node_pseudonym == "US-EAST-ALLIANCE-01"
        assert node.trust_tier == "GOV_CERT"
        assert node.consensus_weight == 1.5
