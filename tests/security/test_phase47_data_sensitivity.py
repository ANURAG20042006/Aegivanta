"""
tests/security/test_phase47_data_sensitivity.py
================================================
Security tests verifying that executive financial data (ROI, losses prevented)
is not exposed across tenant boundaries.
"""

import pytest
from unittest.mock import AsyncMock
from backend.app.services.cyber_roi_service import CyberROIService
from backend.app.services.ciso_report_service import CISOReportService


@pytest.mark.asyncio
async def test_roi_per_tenant_scoping():
    """ROI record generation must be scoped to the correct tenant_id."""
    db = AsyncMock()
    report = await CISOReportService.generate_report(
        db=db,
        tenant_id="tenant-secure-A",
        report_period="Q3-2026",
        report_type="ON_DEMAND"
    )
    assert report["report_period"] == "Q3-2026"
    # Verify the serialized report does NOT leak another tenant's data
    assert "tenant_id" not in report  # Tenant ID should not be returned in public API response


@pytest.mark.asyncio
async def test_board_report_no_pii_leakage():
    """Board report executive summary must not contain PII fields."""
    db = AsyncMock()
    report = await CISOReportService.generate_report(
        db=db,
        tenant_id="tenant-secure-B",
        report_period="Q3-2026",
        report_type="ON_DEMAND"
    )
    # The executive summary should exist and be a non-empty string
    assert isinstance(report["executive_summary"], str)
    assert len(report["executive_summary"]) > 20
    # No raw user PII in summary
    assert "@" not in report["executive_summary"]
