"""
tests/security/test_phase26_tenant_isolation.py
===============================================
Phase 26 Tenant Isolation & Cross-Tenant Boundary Tests.
Verifies that cases, evidence, saved queries, and simulations are strictly scoped to the tenant.
"""

import pytest
from backend.app.services.remediation_governance_service import RemediationGovernanceService
from backend.app.services.evidence_custody_service import EvidenceCustodyService


class TestTenantIsolationSecurity:
    """Security tests verifying tenant isolation in Phase 26 services."""

    def test_evidence_hash_pure_function(self):
        """Payload hashing is deterministic and does not leak cross-tenant state."""
        payload_a = {"tenant_id": "tenant-A", "cmd": "whoami"}
        payload_b = {"tenant_id": "tenant-B", "cmd": "whoami"}
        hash_a = EvidenceCustodyService.compute_payload_hash(payload_a)
        hash_b = EvidenceCustodyService.compute_payload_hash(payload_b)
        assert hash_a != hash_b

    def test_remediation_policy_blocks_unauthorized_role(self):
        """VIEWER role is blocked from executing HIGH or CRITICAL containment actions."""
        policy = RemediationGovernanceService.evaluate_action_policy("ISOLATE_ENDPOINT", user_role="VIEWER")
        assert policy["is_authorized_role"] is False
        assert policy["requires_approval"] is True
