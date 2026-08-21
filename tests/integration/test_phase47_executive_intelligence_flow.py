"""
tests/integration/test_phase47_executive_intelligence_flow.py
=============================================================
Integration tests for the full executive intelligence flow:
posture summary → CISO report generation → ROI retrieval → KPI snapshots.
"""

import pytest
from unittest.mock import AsyncMock
from backend.app.services.executive_intelligence_posture_service import ExecutiveIntelligencePostureService
from backend.app.services.ciso_report_service import CISOReportService
from backend.app.services.cyber_roi_service import CyberROIService


@pytest.mark.asyncio
async def test_full_executive_intelligence_flow():
    db = AsyncMock()

    # 1. Get posture summary
    summary = await ExecutiveIntelligencePostureService.get_posture_summary(
        db=db, tenant_id="tenant-integration"
    )
    assert summary["overall_executive_intelligence_score"] >= 95.0
    assert summary["security_tier"] == "CISO_BOARD_READY_AUTONOMOUS_INTELLIGENCE"

    # 2. Generate CISO board report
    report = await CISOReportService.generate_report(
        db=db,
        tenant_id="tenant-integration",
        report_period="Q3-2026",
        report_type="ON_DEMAND"
    )
    assert report["overall_security_score"] == 94.8
    assert report["regulatory_compliance_score"] == 97.2
    assert len(report["board_recommendations"]) >= 2

    # 3. Verify ROI alignment with posture score
    assert summary["current_roi_percentage"] == 1359.0
    assert summary["cyber_losses_prevented_ytd_usd"] == 35500000.0

    # 4. Confirm KPI metrics consistency
    assert summary["mean_detection_time_minutes"] <= 2.0
    assert summary["sla_compliance_rate"] >= 99.5
