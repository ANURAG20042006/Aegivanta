"""
tests/unit/test_phase29_sbom_engine.py
======================================
Phase 29 Software Bill of Materials (SBOM 2.0) Unit Tests.
"""

import pytest
from backend.app.models.supply_chain import SBOMCatalogItem


class TestSBOMEngine:
    """Unit tests for SBOM dependency catalog items and ecosystem resolution."""

    def test_sbom_catalog_model_initialization(self):
        """SBOMCatalogItem must initialize with package name, version, and license identifier."""
        item = SBOMCatalogItem(
            tenant_id="tenant-123",
            package_name="cryptography",
            version="42.0.5",
            purl="pkg:pypi/cryptography@42.0.5",
            ecosystem="PYPI",
            is_direct_dependency=True,
            license_spdx_id="Apache-2.0",
            is_copyleft=False,
            sha256_checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )
        assert item.package_name == "cryptography"
        assert item.ecosystem == "PYPI"
        assert item.is_copyleft is False
