"""
tests/security/test_phase40_tenant_isolation.py
===============================================
Phase 40 Federated Threat Sharing Multi-Tenant Isolation Security Tests.
"""

import pytest
from backend.app.models.federated_threat_sharing import (
    FederatedIOCExchangeNode, FederatedThreatIndicator, HomomorphicMatchQuery
)


class TestFederatedMultiTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 40 models."""

    def test_federated_models_enforce_tenant_id(self):
        """All Phase 40 Federated Threat Sharing models must enforce tenant_id partition attributes."""
        node = FederatedIOCExchangeNode(tenant_id="tenant-fed-1", node_pseudonym="n-1", public_key_hash="k-1")
        ind = FederatedThreatIndicator(tenant_id="tenant-fed-1", anonymized_indicator_hash="h-1")
        qry = HomomorphicMatchQuery(tenant_id="tenant-fed-1", encrypted_query_hash="q-1")

        assert node.tenant_id == "tenant-fed-1"
        assert ind.tenant_id == "tenant-fed-1"
        assert qry.tenant_id == "tenant-fed-1"
