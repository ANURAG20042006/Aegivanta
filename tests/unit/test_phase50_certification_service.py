"""
tests/unit/test_phase50_certification_service.py
================================================
Unit tests for EnterpriseCertificationService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.enterprise_certification_service import EnterpriseCertificationService
from backend.app.models.global_enterprise_certification import (
    EnterpriseCertificationBadge,
    AutonomousDefenseAttestation
)


@pytest.mark.asyncio
async def test_generate_attestation():
    db = AsyncMock()
    att = await EnterpriseCertificationService.generate_attestation(
        db=db,
        tenant_id="tenant-cert-test"
    )
    assert "ATTEST-2026-AEGIVANTA" in att["attestation_serial"]
    assert att["platform_version"] == "v50.0.0-ENTERPRISE-CERTIFIED"
    assert len(att["sha256_integrity_hash"]) == 64
    assert att["overall_posture_score"] == 99.9
    assert att["claims"]["phases_completed"] == 50
    assert att["claims"]["multi_tenancy_verified"] is True


@pytest.mark.asyncio
async def test_list_certifications_with_mock():
    db = AsyncMock()
    mock_badge = EnterpriseCertificationBadge(
        id="badge-1",
        tenant_id="tenant-cert-test",
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
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_badge]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    certs = await EnterpriseCertificationService.list_certifications(
        db=db, tenant_id="tenant-cert-test"
    )
    assert isinstance(certs, list)
    assert len(certs) >= 1
    assert certs[0]["framework_code"] == "FEDRAMP_HIGH"
    assert certs[0]["compliance_score"] == 99.8
