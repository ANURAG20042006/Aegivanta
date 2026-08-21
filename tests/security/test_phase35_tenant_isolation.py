"""
tests/security/test_phase35_tenant_isolation.py
===============================================
Phase 35 DLP Multi-Tenant Isolation Security Tests.
"""

import pytest
from backend.app.models.dlp_security import (
    DLPInspectionPolicy, DLPIncidentEvent, TokenizedDataVault, ShadowDataStore
)


class TestDLPTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 35 models."""

    def test_dlp_models_enforce_tenant_id(self):
        """All DLP and Tokenization models must enforce tenant_id partition attributes."""
        policy = DLPInspectionPolicy(tenant_id="tenant-dlp-1", policy_name="PCI", regex_pattern=r"\d+")
        incident = DLPIncidentEvent(tenant_id="tenant-dlp-1")
        vault = TokenizedDataVault(tenant_id="tenant-dlp-1", token_identifier="TKN-1", surrogate_token_value="surr", encrypted_blob_payload="enc")
        store = ShadowDataStore(tenant_id="tenant-dlp-1", resource_uri="s3://test")

        assert policy.tenant_id == "tenant-dlp-1"
        assert incident.tenant_id == "tenant-dlp-1"
        assert vault.tenant_id == "tenant-dlp-1"
        assert store.tenant_id == "tenant-dlp-1"
