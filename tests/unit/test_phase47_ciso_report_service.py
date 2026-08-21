"""
tests/unit/test_phase47_ciso_report_service.py
==============================================
Unit tests for CISOReportService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.ciso_report_service import CISOReportService
from backend.app.models.executive_security_intelligence import CISOBoardReport


@pytest.mark.asyncio
async def test_generate_report():
    db = AsyncMock()
    report = await CISOReportService.generate_report(
        db=db,
        tenant_id="tenant-exec",
        report_period="Q3-2026",
        report_type="ON_DEMAND"
    )
    assert report["report_period"] == "Q3-2026"
    assert report["report_type"] == "ON_DEMAND"
    assert report["overall_security_score"] == 94.8
    assert report["regulatory_compliance_score"] == 97.2
    assert report["risk_posture_trend"] == "IMPROVING"
    assert len(report["board_recommendations"]) == 3


@pytest.mark.asyncio
async def test_list_reports_with_mock():
    db = AsyncMock()
    mock_report = CISOBoardReport(
        id="rpt-1",
        tenant_id="tenant-exec",
        report_period="Q3-2026",
        report_type="QUARTERLY",
        overall_security_score=94.8,
        risk_posture_trend="IMPROVING",
        regulatory_compliance_score=97.2,
        mttr_days=0.08,
        incidents_prevented_count=1847,
        executive_summary="Test summary.",
        board_recommendations_json=["Rec 1", "Rec 2"],
        kpi_breakdown_json={"threats": 58492}
    )

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_report]
    mock_scalars.first.return_value = mock_report
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    reports = await CISOReportService.list_reports(db=db, tenant_id="tenant-exec")
    assert isinstance(reports, list)
    assert len(reports) >= 1
    assert reports[0]["report_period"] == "Q3-2026"
    assert reports[0]["overall_security_score"] == 94.8
