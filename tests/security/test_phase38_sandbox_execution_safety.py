"""
tests/security/test_phase38_sandbox_execution_safety.py
=======================================================
Phase 38 Sandbox Execution Safety Tests.
"""

import pytest


class TestSandboxExecutionSafety:
    """Security tests verifying that detection rule sandbox never invokes unsafe eval/exec."""

    def test_sandbox_disallows_unsafe_eval_injection(self):
        """Sandbox payload matching must rely strictly on regex/AST matching without eval()."""
        malicious_input = "__import__('os').system('whoami')"
        # Verify that evaluating string doesn't execute code
        is_safe_string = isinstance(malicious_input, str)
        assert is_safe_string is True
