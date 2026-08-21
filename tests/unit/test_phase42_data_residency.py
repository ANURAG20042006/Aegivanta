"""
tests/unit/test_phase42_data_residency.py
=========================================
Phase 42 Data Residency Boundary Unit Tests.
"""

import pytest
from backend.app.models.multi_region_resilience import DataResidencyBoundary


class TestDataResidency:
    """Unit tests for DataResidencyBoundary model."""

    def test_residency_boundary_model_creation(self):
        """DataResidencyBoundary must store name, standard, and enforced regions."""
        bnd = DataResidencyBoundary(
            tenant_id="tenant-multi",
            boundary_name="European Union Sovereign Vault",
            compliance_standard="GDPR_EU_ONLY",
            enforced_regions="EU_WEST_1,EU_CENTRAL_1",
            strict_egress_block=True,
            enabled=True
        )
        assert bnd.compliance_standard == "GDPR_EU_ONLY"
        assert bnd.strict_egress_block is True
        assert "EU_WEST_1" in bnd.enforced_regions
