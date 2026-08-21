"""
tests/unit/test_phase38_compliance_posture.py
=============================================
Phase 38 Compliance Posture & Control Assessment Unit Tests.
"""

import pytest
from backend.app.models.compliance_detection_eng import ComplianceFrameworkControl


class TestCompliancePosture:
    """Unit tests for ComplianceFrameworkControl model."""

    def test_compliance_control_model(self):
        """ComplianceFrameworkControl must track framework, control ID, status, and evidence."""
        ctrl = ComplianceFrameworkControl(
            tenant_id="tenant-comp",
            framework="SOC2_TYPE2",
            control_id="CC6.1",
            control_title="Access Control & MFA",
            compliance_status="PASS_COMPLIANT",
            automated_evidence_summary="100% MFA enrollment verified across directory."
        )
        assert ctrl.framework == "SOC2_TYPE2"
        assert ctrl.control_id == "CC6.1"
        assert ctrl.compliance_status == "PASS_COMPLIANT"
