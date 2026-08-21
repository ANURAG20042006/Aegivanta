"""
tests/unit/test_phase38_evidence_collector.py
=============================================
Phase 38 Compliance Audit Report & Attestation Unit Tests.
"""

import pytest
from backend.app.models.compliance_detection_eng import ComplianceAuditReport


class TestEvidenceCollector:
    """Unit tests for ComplianceAuditReport model."""

    def test_audit_report_model(self):
        """ComplianceAuditReport must store framework, score, attestation hash, and date."""
        report = ComplianceAuditReport(
            tenant_id="tenant-comp",
            framework="ISO_27001",
            overall_compliance_score=98.5,
            passing_controls_count=48,
            failing_controls_count=0,
            auditor_attestation_hash="abcdef1234567890abcdef1234567890",
            generated_by="officer_01"
        )
        assert report.framework == "ISO_27001"
        assert report.overall_compliance_score == 98.5
        assert len(report.auditor_attestation_hash) == 32
