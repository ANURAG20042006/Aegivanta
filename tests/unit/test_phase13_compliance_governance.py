"""
tests/unit/test_phase13_compliance_governance.py
================================================
Unit tests for Governance & Regulatory Compliance Mapping (SOC 2, ISO 27001, GDPR, NIST CSF).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.compliance_service import ComplianceService
from backend.app.models.security_policy import SecurityPolicy


@pytest.mark.asyncio
async def test_get_compliance_posture():
    """Validates control evaluation across SOC 2, ISO 27001, GDPR, and NIST CSF."""
    db = AsyncMock()
    mock_policy = SecurityPolicy(organization_id="org-prod", require_mfa=True, ip_allowlist={"ips": ["10.0.0.0/8"]})

    res_mfa = MagicMock(scalar=MagicMock(return_value=5))
    res_pol = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_policy))

    db.execute = AsyncMock(side_effect=[res_mfa, res_pol])

    posture = await ComplianceService.get_compliance_posture(db, "org-prod")

    assert posture["organization_id"] == "org-prod"
    assert posture["overall_readiness_score"] >= 90
    assert "SOC_2_TYPE_II" in posture["frameworks"]
    assert "ISO_27001_2022" in posture["frameworks"]
    assert "GDPR" in posture["frameworks"]
    assert "NIST_CSF_V2" in posture["frameworks"]
    assert posture["frameworks"]["SOC_2_TYPE_II"]["controls"][0]["status"] == "COMPLIANT"
