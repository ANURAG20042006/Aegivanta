"""
tests/security/test_phase27_tenant_isolation.py
===============================================
Phase 27 CNAPP Multi-Tenant Boundary Security Tests.
"""

import pytest
from backend.app.models.cloud_security import CloudAccount, CloudWorkloadFinding, ServerlessFunctionRisk


class TestCNAPPTenantIsolation:
    """Security tests verifying tenant boundaries across cloud models."""

    def test_cloud_models_require_tenant_id(self):
        """All CNAPP models must have tenant_id attribute for multi-tenant partitioning."""
        acc = CloudAccount(tenant_id="tenant-A", provider="AWS", account_name="A", account_identifier="1", auth_type="ASSUME_ROLE", encrypted_credentials="enc")
        cwpp = CloudWorkloadFinding(tenant_id="tenant-A", workload_type="VM", workload_id="1", workload_name="vm", threat_type="REVERSE_SHELL")
        srv = ServerlessFunctionRisk(tenant_id="tenant-A", provider="AWS", function_arn="arn", function_name="fn", runtime="py311", remediation_advice="none")

        assert acc.tenant_id == "tenant-A"
        assert cwpp.tenant_id == "tenant-A"
        assert srv.tenant_id == "tenant-A"
