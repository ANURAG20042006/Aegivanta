"""
tests/unit/test_phase43_legal_hold.py
=====================================
Phase 43 Forensic Legal Hold Unit Tests.
"""

import pytest
from backend.app.models.data_governance_dsar import LegalHoldOrder


class TestLegalHold:
    """Unit tests for LegalHoldOrder model."""

    def test_legal_hold_model_creation(self):
        """LegalHoldOrder must store matter reference, custodian, and scope."""
        hold = LegalHoldOrder(
            tenant_id="tenant-gov",
            matter_reference="MATTER-2026-SEC-01",
            custodian_name="General Counsel",
            scope_pattern="CASE_FORENSICS_*",
            status="ACTIVE_HOLD",
            frozen_artifact_count=42
        )
        assert hold.matter_reference == "MATTER-2026-SEC-01"
        assert hold.custodian_name == "General Counsel"
        assert hold.frozen_artifact_count == 42
