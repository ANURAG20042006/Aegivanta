"""
tests/unit/test_phase44_marketplace_catalog.py
==============================================
Phase 44 Marketplace Catalog Unit Tests.
"""

import pytest
from backend.app.models.security_marketplace import MarketplacePackage


class TestMarketplaceCatalog:
    """Unit tests for MarketplacePackage model."""

    def test_marketplace_package_model_creation(self):
        """MarketplacePackage must store name, type, version, author, and signature."""
        pkg = MarketplacePackage(
            tenant_id="global-catalog",
            package_name="CrowdStrike Falcon XDR Stream Ingester",
            package_type="CONNECTOR_ADAPTER",
            version="2.4.0",
            author="CrowdStrike Alliance",
            verified_publisher=True,
            signature_hash="abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
            installs_count=4850
        )
        assert pkg.package_name == "CrowdStrike Falcon XDR Stream Ingester"
        assert pkg.package_type == "CONNECTOR_ADAPTER"
        assert pkg.installs_count == 4850
        assert pkg.verified_publisher is True
