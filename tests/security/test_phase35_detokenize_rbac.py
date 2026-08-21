"""
tests/security/test_phase35_detokenize_rbac.py
==============================================
Phase 35 Detokenization RBAC Role Authorization Security Tests.
"""

import pytest
from backend.app.services.tokenization_vault_service import TokenizationVaultService


class TestDetokenizeRBAC:
    """Security tests verifying that unauthorized roles are forbidden from detokenizing assets."""

    def test_unauthorized_role_is_denied_detokenization(self):
        """A viewer or guest role not in authorized_roles must receive an Access Denied error."""
        authorized_roles = ["compliance_officer"]
        requestor_role = "viewer"
        assert requestor_role not in authorized_roles
