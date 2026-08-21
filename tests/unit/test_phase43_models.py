"""
tests/unit/test_phase43_models.py
=================================
Phase 43 Model Schema & Attributes Unit Tests.
"""

import pytest
from backend.app.models.data_governance_dsar import (
    DataLineageRecord, LegalHoldOrder, DSARPrivacyRequest
)


class TestPhase43Models:
    """Unit tests verifying Phase 43 database attributes."""

    def test_lineage_stage_attributes(self):
        """Data lineage record should store stage and record count."""
        lin = DataLineageRecord(
            tenant_id="tenant-gov",
            data_asset_name="Cold Archive WORM Vault",
            pipeline_stage="COLD_ARCHIVE",
            transform_hash="hash-cold-123",
            record_count=920000
        )
        assert lin.pipeline_stage == "COLD_ARCHIVE"
        assert lin.record_count == 920000
