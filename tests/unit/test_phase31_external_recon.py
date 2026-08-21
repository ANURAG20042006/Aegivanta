"""
tests/unit/test_phase31_external_recon.py
=========================================
Phase 31 External Recon & Asset Discovery Unit Tests.
"""

import pytest
from backend.app.models.attack_surface import ExternalAsset


class TestExternalRecon:
    """Unit tests for external perimeter asset discovery models."""

    def test_external_asset_model_initialization(self):
        """ExternalAsset must store FQDN, open ports, SSL health, and cloud provider."""
        asset = ExternalAsset(
            tenant_id="tenant-123",
            fqdn_or_ip="api.aegivanta.io",
            asset_type="SUBDOMAIN",
            primary_ip="198.51.100.12",
            asn_organization="AS16509 Amazon.com, Inc.",
            cloud_provider="AWS",
            open_ports=[80, 443],
            ssl_issuer="DigiCert Global Root G2",
            ssl_days_until_expiry=120,
            ssl_has_weak_ciphers=False,
            risk_score=15.0,
            status="ACTIVE"
        )
        assert asset.fqdn_or_ip == "api.aegivanta.io"
        assert asset.cloud_provider == "AWS"
        assert 443 in asset.open_ports
        assert asset.ssl_days_until_expiry == 120
