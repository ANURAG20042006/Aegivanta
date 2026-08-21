"""
tests/unit/test_phase44_package_installer.py
============================================
Phase 44 Sandboxed Package Installer Unit Tests.
"""

import pytest
from backend.app.models.security_marketplace import InstalledExtension


class TestPackageInstaller:
    """Unit tests for InstalledExtension model."""

    def test_installed_extension_model_creation(self):
        """InstalledExtension must store tenant, package_id, name, version, and enabled status."""
        ext = InstalledExtension(
            tenant_id="tenant-mkt",
            package_id="pkg-123",
            package_name="APT29 & FIN7 High-Fidelity Sigma Detection Pack",
            installed_version="3.1.2",
            auto_update=True,
            enabled=True
        )
        assert ext.package_name == "APT29 & FIN7 High-Fidelity Sigma Detection Pack"
        assert ext.installed_version == "3.1.2"
        assert ext.enabled is True
