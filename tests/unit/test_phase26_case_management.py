"""
tests/unit/test_phase26_case_management.py
==========================================
Phase 26.6 Enterprise SOC Case Management Unit Tests.
"""

import pytest
from backend.app.models.soc_case import SOC_CASE_STATUSES, SOC_CASE_PRIORITIES


class TestSOCCaseManagement:
    """Unit tests for SOC Case Management statuses and state transitions."""

    def test_nine_case_statuses_defined(self):
        """All 9 required case statuses must exist in status catalog."""
        required = {
            "OPEN", "TRIAGED", "INVESTIGATING", "CONTAINMENT",
            "REMEDIATION", "MONITORING", "RESOLVED", "CLOSED", "REOPENED"
        }
        assert set(SOC_CASE_STATUSES) == required

    def test_priorities_defined(self):
        """Standard 4 priority levels must exist."""
        assert set(SOC_CASE_PRIORITIES) == {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
