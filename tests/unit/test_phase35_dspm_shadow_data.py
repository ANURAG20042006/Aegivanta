"""
tests/unit/test_phase35_dspm_shadow_data.py
===========================================
Phase 35 DSPM Shadow Data Store Discovery Unit Tests.
"""

import pytest
from backend.app.models.dlp_security import ShadowDataStore


class TestDSPMShadowData:
    """Unit tests for ShadowDataStore discovery entities."""

    def test_shadow_data_store_model(self):
        """ShadowDataStore must record storage URI, provider, record count, and risk level."""
        store = ShadowDataStore(
            tenant_id="tenant-dlp",
            resource_uri="s3://backup-unencrypted-2026",
            storage_provider="AWS_S3",
            discovered_sensitive_records_count=50000,
            detected_data_categories=["PII_SSN"],
            encryption_state="UNENCRYPTED_PUBLIC",
            risk_level="CRITICAL"
        )
        assert store.resource_uri == "s3://backup-unencrypted-2026"
        assert store.discovered_sensitive_records_count == 50000
        assert store.risk_level == "CRITICAL"
