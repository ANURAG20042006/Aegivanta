"""
tests/unit/test_phase34_virtual_patching.py
===========================================
Phase 34 Virtual Patching & Compensating Controls Unit Tests.
"""

import pytest
from backend.app.models.vulnerability_mgmt import VirtualPatchRule


class TestVirtualPatching:
    """Unit tests for Virtual Patch rule schemas."""

    def test_virtual_patch_rule_model(self):
        """VirtualPatchRule must store CVE ID, rule type, syntax, and block counter."""
        rule = VirtualPatchRule(
            tenant_id="tenant-123",
            cve_id="CVE-2024-3400",
            rule_name="VP-PANOS-01",
            rule_type="AWS_WAF",
            rule_syntax='{"Name": "BlockPANOS"}',
            status="ACTIVE_ENFORCING",
            total_blocked_requests_count=45
        )
        assert rule.cve_id == "CVE-2024-3400"
        assert rule.rule_type == "AWS_WAF"
        assert rule.total_blocked_requests_count == 45
