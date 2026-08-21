"""
tests/unit/test_phase43_data_lineage.py
=======================================
Phase 43 Data Lineage Unit Tests.
"""

import pytest
from backend.app.models.data_governance_dsar import DataLineageRecord


class TestDataLineage:
    """Unit tests for DataLineageRecord model."""

    def test_lineage_record_model_creation(self):
        """DataLineageRecord must store asset name, stage, and transform hash."""
        lin = DataLineageRecord(
            tenant_id="tenant-gov",
            data_asset_name="Telemetry Stream Raw Ingress",
            pipeline_stage="SENSOR_INGRESS",
            transform_hash="abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
            record_count=850000
        )
        assert lin.data_asset_name == "Telemetry Stream Raw Ingress"
        assert lin.pipeline_stage == "SENSOR_INGRESS"
        assert lin.record_count == 850000
