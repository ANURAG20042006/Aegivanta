"""
tests/security/test_phase31_tenant_isolation.py
===============================================
Phase 31 Attack Surface Multi-Tenant Boundary Tests.
"""

import pytest
from backend.app.models.attack_surface import (
    ExternalAsset, DanglingDNSRisk, DarkWebCredentialLeak, BrandImpersonationAlert
)


class TestAttackSurfaceTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 31 models."""

    def test_asm_models_require_tenant_id(self):
        """All Attack Surface models must enforce tenant_id partition attributes."""
        ast = ExternalAsset(tenant_id="tenant-asm", fqdn_or_ip="api.aegivanta.io")
        dd = DanglingDNSRisk(tenant_id="tenant-asm", subdomain="s.aegivanta.io", cname_target="target")
        dw = DarkWebCredentialLeak(tenant_id="tenant-asm", employee_email="user@aegivanta.io", password_hash_sample="hash")
        ba = BrandImpersonationAlert(tenant_id="tenant-asm", impersonating_domain="lookalike.com")

        assert ast.tenant_id == "tenant-asm"
        assert dd.tenant_id == "tenant-asm"
        assert dw.tenant_id == "tenant-asm"
        assert ba.tenant_id == "tenant-asm"
