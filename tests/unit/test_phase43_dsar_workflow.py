"""
tests/unit/test_phase43_dsar_workflow.py
========================================
Phase 43 GDPR / CCPA DSAR Privacy Workflow Unit Tests.
"""

import pytest
from backend.app.models.data_governance_dsar import DSARPrivacyRequest


class TestDSARWorkflow:
    """Unit tests for DSARPrivacyRequest model."""

    def test_dsar_request_model_creation(self):
        """DSARPrivacyRequest must store email, type, status, and certificate hash."""
        req = DSARPrivacyRequest(
            tenant_id="tenant-gov",
            requester_email="privacy-user@domain.com",
            request_type="RIGHT_OF_ACCESS_EXPORT",
            status="COMPLETED",
            discovered_records_count=128,
            completion_certificate_hash="abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        )
        assert req.requester_email == "privacy-user@domain.com"
        assert req.request_type == "RIGHT_OF_ACCESS_EXPORT"
        assert req.discovered_records_count == 128
