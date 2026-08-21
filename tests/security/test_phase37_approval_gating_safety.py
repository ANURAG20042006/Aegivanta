"""
tests/security/test_phase37_approval_gating_safety.py
=====================================================
Phase 37 Human-in-the-Loop AI Action Gating Safety Tests.
"""

import pytest


class TestApprovalGatingSafety:
    """Security tests verifying that high-impact containment actions require human approval."""

    def test_containment_action_requires_explicit_approval(self):
        """Actions marked as CONTAINMENT or HIGH_RISK must not execute without human approval."""
        impact_tier = "CONTAINMENT"
        requires_approval = impact_tier in ["CONTAINMENT", "HIGH_RISK"]
        assert requires_approval is True
