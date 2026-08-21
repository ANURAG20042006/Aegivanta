"""
tests/security/test_phase28_tenant_isolation.py
===============================================
Phase 28 Enterprise IAM Multi-Tenant Boundary Security Tests.
"""

import pytest
from backend.app.models.identity import PAMSessionElevation, IdentityThreatDetection, PasskeyCredential, IdentityScorecard


class TestEnterpriseIAMTenantIsolation:
    """Security tests verifying tenant boundaries across IAM models."""

    def test_iam_models_require_tenant_id(self):
        """All Phase 28 models must have tenant_id attribute for multi-tenant partitioning."""
        pam = PAMSessionElevation(tenant_id="tenant-A", user_id="1", username="u", target_role="ADMIN", target_resource="res", justification="just")
        itdr = IdentityThreatDetection(tenant_id="tenant-A", threat_type="MFA_FATIGUE", target_username="u", source_ip="1.2.3.4")
        key = PasskeyCredential(tenant_id="tenant-A", user_id="1", credential_id="c1", public_key_pem="pem")
        sc = IdentityScorecard(tenant_id="tenant-A", user_id="1", username="u")

        assert pam.tenant_id == "tenant-A"
        assert itdr.tenant_id == "tenant-A"
        assert key.tenant_id == "tenant-A"
        assert sc.tenant_id == "tenant-A"
