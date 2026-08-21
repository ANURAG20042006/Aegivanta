"""
tests/unit/test_phase47_posture_service.py
==========================================
Unit tests for ExecutiveIntelligencePostureService.
"""

import pytest
from unittest.mock import AsyncMock
from backend.app.services.executive_intelligence_posture_service import ExecutiveIntelligencePostureService


@pytest.mark.asyncio
async def test_get_posture_summary():
    db = AsyncMock()
    summary = await ExecutiveIntelligencePostureService.get_posture_summary(
        db=db, tenant_id="tenant-exec"
    )
    assert summary["overall_executive_intelligence_score"] >= 95.0
    assert summary["security_tier"] == "CISO_BOARD_READY_AUTONOMOUS_INTELLIGENCE"
    assert summary["current_roi_percentage"] == 1359.0
    assert summary["current_security_posture_score"] == 94.8
    assert summary["regulatory_compliance_score"] == 97.2
    assert summary["automation_coverage_percentage"] == 84.0
    assert summary["mean_detection_time_minutes"] == 1.4
    assert summary["sla_compliance_rate"] == 99.91
    assert len(summary["top_executive_priorities"]) == 3


@pytest.mark.asyncio
async def test_posture_ytd_metrics():
    db = AsyncMock()
    summary = await ExecutiveIntelligencePostureService.get_posture_summary(
        db=db, tenant_id="tenant-exec"
    )
    assert summary["cyber_losses_prevented_ytd_usd"] == 35500000.0
    assert summary["threats_blocked_ytd"] == 187241
