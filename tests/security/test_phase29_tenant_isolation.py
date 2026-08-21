"""
tests/security/test_phase29_tenant_isolation.py
===============================================
Phase 29 Supply Chain Security Multi-Tenant Boundary Tests.
"""

import pytest
from backend.app.models.supply_chain import (
    SBOMCatalogItem, VEXStatement, SLSAPipelineAttestation, PipelineSecurityGate
)


class TestSupplyChainTenantIsolation:
    """Security tests verifying tenant boundaries across Supply Chain models."""

    def test_supply_chain_models_require_tenant_id(self):
        """All Phase 29 models must have tenant_id attribute for multi-tenant isolation."""
        sbom = SBOMCatalogItem(tenant_id="tenant-A", package_name="pkg", version="1.0", purl="pkg:npm/pkg@1.0", ecosystem="NPM", sha256_checksum="sha")
        vex = VEXStatement(tenant_id="tenant-A", vulnerability_id="CVE-2026-1", product_purl="purl", status="NOT_AFFECTED", impact_statement="none")
        slsa = SLSAPipelineAttestation(tenant_id="tenant-A", artifact_name="art", artifact_digest="dig", build_invocation_id="inv", cosign_signature="sig", source_commit_sha="sha")
        gate = PipelineSecurityGate(tenant_id="tenant-A", gate_name="g1")

        assert sbom.tenant_id == "tenant-A"
        assert vex.tenant_id == "tenant-A"
        assert slsa.tenant_id == "tenant-A"
        assert gate.tenant_id == "tenant-A"
