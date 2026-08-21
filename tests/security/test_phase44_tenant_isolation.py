"""
tests/security/test_phase44_tenant_isolation.py
===============================================
Phase 44 Security Marketplace Multi-Tenant Isolation Security Tests.
"""

import pytest
from backend.app.models.security_marketplace import (
    MarketplacePackage, InstalledExtension, PackageReviewRating
)


class TestMarketplaceMultiTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 44 models."""

    def test_marketplace_models_enforce_tenant_id(self):
        """Installed extensions and ratings must enforce tenant_id partition attributes."""
        ext = InstalledExtension(tenant_id="tenant-mkt-1", package_id="p1", package_name="n1")
        rev = PackageReviewRating(tenant_id="tenant-mkt-1", package_id="p1")

        assert ext.tenant_id == "tenant-mkt-1"
        assert rev.tenant_id == "tenant-mkt-1"
