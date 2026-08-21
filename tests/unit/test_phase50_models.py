"""
tests/unit/test_phase50_models.py
=================================
Unit tests for Phase 50 Global Enterprise Certification models.
"""

from backend.app.models.global_enterprise_certification import (
    EnterpriseCertificationBadge,
    ProductionReadinessGate,
    AutonomousDefenseAttestation
)


def test_enterprise_certification_badge_model():
    badge = EnterpriseCertificationBadge(
        tenant_id="tenant-cert-1",
        framework_name="FedRAMP High",
        framework_code="FEDRAMP_HIGH",
        compliance_score=99.8,
        audit_status="CERTIFIED",
        auditor_organization="Coalfire Systems",
        certificate_id="CERT-FEDRAMP-2026-AEGIS-001",
        controls_evaluated_count=421,
        controls_passed_count=421,
        findings_count=0
    )
    assert badge.framework_code == "FEDRAMP_HIGH"
    assert badge.compliance_score == 99.8
    assert badge.controls_passed_count == 421
    assert badge.findings_count == 0


def test_production_readiness_gate_model():
    gate = ProductionReadinessGate(
        tenant_id="tenant-cert-1",
        gate_name="Global Multi-Region Autonomous Failover",
        gate_category="RESILIENCE",
        phase_origin="Phase 42",
        status="PASSED",
        benchmark_value="RTO < 30s",
        measured_value="RTO = 8.4s",
        is_critical_blocker=True
    )
    assert gate.gate_name == "Global Multi-Region Autonomous Failover"
    assert gate.status == "PASSED"
    assert gate.is_critical_blocker is True


def test_autonomous_defense_attestation_model():
    attestation = AutonomousDefenseAttestation(
        tenant_id="tenant-cert-1",
        attestation_serial="ATTEST-2026-AEGIVANTA-ALPHA-50",
        platform_version="v50.0.0-ENTERPRISE-CERTIFIED",
        signing_key_id="kms/aegivanta-root-hsm-2026",
        sha256_integrity_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        signature_hex="3045022100...",
        overall_posture_score=99.9,
        attested_by="AEGIVANTA Sovereign Root HSM"
    )
    assert attestation.attestation_serial == "ATTEST-2026-AEGIVANTA-ALPHA-50"
    assert attestation.platform_version == "v50.0.0-ENTERPRISE-CERTIFIED"
    assert attestation.overall_posture_score == 99.9
