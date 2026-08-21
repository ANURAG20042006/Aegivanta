"""
tests/unit/test_phase44_models.py
=================================
Phase 44 Model Schema & Attributes Unit Tests.
"""

import pytest
from backend.app.models.security_marketplace import (
    MarketplacePackage, InstalledExtension, PackageReviewRating
)


class TestPhase44Models:
    """Unit tests verifying Phase 44 database attributes."""

    def test_marketplace_package_attributes(self):
        """Marketplace package should store AI_AGENT_SKILL category."""
        pkg = MarketplacePackage(
            tenant_id="global-catalog",
            package_name="Autonomous Threat Forecaster",
            package_type="AI_AGENT_SKILL",
            signature_hash="sig-123"
        )
        assert pkg.package_type == "AI_AGENT_SKILL"
        assert pkg.signature_hash == "sig-123"
