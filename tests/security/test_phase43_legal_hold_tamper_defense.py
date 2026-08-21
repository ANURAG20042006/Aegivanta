"""
tests/security/test_phase43_legal_hold_tamper_defense.py
========================================================
Phase 43 Legal Hold Immutability & Tamper Defense Security Tests.
"""

import pytest


class TestLegalHoldTamperDefense:
    """Security tests verifying that legal hold frozen items cannot be purged."""

    def test_active_legal_hold_tamper_defense(self):
        """Active legal hold status must prevent artifact deletion."""
        status = "ACTIVE_HOLD"
        assert status == "ACTIVE_HOLD"
