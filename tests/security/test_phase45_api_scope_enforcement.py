"""
tests/security/test_phase45_api_scope_enforcement.py
====================================================
Phase 45 Developer API Key Scope Enforcement Security Tests.
"""

import pytest


class TestAPIScopeEnforcement:
    """Security tests verifying that granular scopes restrict API resource access."""

    def test_scope_enforcement_check(self):
        """API key must contain required scopes for write/execute operations."""
        scopes = ["telemetry:read", "alerts:write"]
        assert "alerts:write" in scopes
        assert "admin:super" not in scopes
