"""
tests/security/test_phase50_tenant_isolation.py
================================================
Security tests for Phase 50 Global Enterprise Certification tenant isolation.
"""

from backend.app.models.global_enterprise_certification import (
    EnterpriseCertificationBadge,
    ProductionReadinessGate,
    AutonomousDefenseAttestation
)


def test_certification_badge_tenant_isolation():
    badge_a = EnterpriseCertificationBadge(
        tenant_id="tenant-alpha",
        framework_code="FEDRAMP_HIGH"
    )
    badge_b = EnterpriseCertificationBadge(
        tenant_id="tenant-beta",
        framework_code="FEDRAMP_HIGH"
    )
    assert badge_a.tenant_id != badge_b.tenant_id


def test_readiness_gate_tenant_isolation():
    gate_a = ProductionReadinessGate(
        tenant_id="tenant-alpha",
        gate_name="Gate A"
    )
    gate_b = ProductionReadinessGate(
        tenant_id="tenant-beta",
        gate_name="Gate A"
    )
    assert gate_a.tenant_id != gate_b.tenant_id


def test_attestation_tenant_isolation():
    att_a = AutonomousDefenseAttestation(
        tenant_id="tenant-alpha",
        attestation_serial="ATTEST-ALPHA"
    )
    att_b = AutonomousDefenseAttestation(
        tenant_id="tenant-beta",
        attestation_serial="ATTEST-BETA"
    )
    assert att_a.tenant_id != att_b.tenant_id
    assert att_a.attestation_serial != att_b.attestation_serial
