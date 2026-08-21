"""
tests/unit/test_phase47_cyber_roi_service.py
============================================
Unit tests for CyberROIService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.cyber_roi_service import CyberROIService
from backend.app.models.executive_security_intelligence import CyberROIRecord


@pytest.mark.asyncio
async def test_list_roi_with_mock():
    db = AsyncMock()
    mock_roi = CyberROIRecord(
        id="roi-1",
        tenant_id="tenant-exec",
        period_label="Q3-2026",
        security_investment_usd=850000.0,
        estimated_losses_prevented_usd=12400000.0,
        roi_percentage=1359.0,
        breach_probability_reduction=0.87,
        cyber_insurance_savings_usd=145000.0,
        compliance_penalty_avoidance_usd=3200000.0,
        automation_labor_savings_usd=520000.0,
        top_roi_drivers_json=["Driver A", "Driver B"]
    )

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_roi]
    mock_scalars.first.return_value = mock_roi
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    records = await CyberROIService.list_roi_records(db=db, tenant_id="tenant-exec")
    assert isinstance(records, list)
    assert len(records) >= 1
    assert records[0]["roi_percentage"] == 1359.0
    assert records[0]["period_label"] == "Q3-2026"
    assert records[0]["estimated_losses_prevented_usd"] == 12400000.0


@pytest.mark.asyncio
async def test_roi_financial_metrics():
    db = AsyncMock()
    mock_roi = CyberROIRecord(
        id="roi-2",
        tenant_id="tenant-exec",
        period_label="Q3-2026",
        security_investment_usd=850000.0,
        estimated_losses_prevented_usd=12400000.0,
        roi_percentage=1359.0,
        breach_probability_reduction=0.87,
        cyber_insurance_savings_usd=145000.0,
        compliance_penalty_avoidance_usd=3200000.0,
        automation_labor_savings_usd=520000.0,
        top_roi_drivers_json=["Automation reduced analyst hours 68%"]
    )
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_roi
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    db.execute.return_value = mock_result

    roi = await CyberROIService.get_latest_roi(db=db, tenant_id="tenant-exec")
    assert roi["breach_probability_reduction"] == 0.87
    assert roi["cyber_insurance_savings_usd"] == 145000.0
    assert roi["compliance_penalty_avoidance_usd"] == 3200000.0
