"""
tests/security/test_phase38_tenant_isolation.py
===============================================
Phase 38 Compliance & Detection Multi-Tenant Isolation Security Tests.
"""

import pytest
from backend.app.models.compliance_detection_eng import (
    AutonomousDetectionRule, ComplianceFrameworkControl, ComplianceAuditReport, DetectionSandboxExecution
)


class TestComplianceMultiTenantIsolation:
    """Security tests verifying tenant isolation attributes across Phase 38 models."""

    def test_compliance_models_enforce_tenant_id(self):
        """All Phase 38 Compliance & Detection models must enforce tenant_id partition attributes."""
        rule = AutonomousDetectionRule(tenant_id="tenant-comp-1", rule_name="r-1", rule_syntax_payload="s-1")
        ctrl = ComplianceFrameworkControl(tenant_id="tenant-comp-1", framework="SOC2_TYPE2", control_id="c-1", control_title="t-1", automated_evidence_summary="e-1")
        report = ComplianceAuditReport(tenant_id="tenant-comp-1", framework="SOC2_TYPE2", auditor_attestation_hash="h-1")
        sandbox = DetectionSandboxExecution(tenant_id="tenant-comp-1", rule_id="r-1", test_event_payload="p-1")

        assert rule.tenant_id == "tenant-comp-1"
        assert ctrl.tenant_id == "tenant-comp-1"
        assert report.tenant_id == "tenant-comp-1"
        assert sandbox.tenant_id == "tenant-comp-1"
