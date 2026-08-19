"""
tests/unit/test_phase3_soc_metrics.py
=====================================
Unit tests for SOC Effectiveness & Workload Analytics.
"""

import pytest
from backend.app.database import AsyncSessionFactory
from backend.app.services.soc_metrics_service import SOCMetricsService


@pytest.mark.asyncio
async def test_soc_overview_kpis():
    """Verify MTTD, MTTR, and compression ratios calculate cleanly."""
    async with AsyncSessionFactory() as db:
        overview = await SOCMetricsService.get_soc_overview(lookback_days=30, db=db)
        assert "mttd_minutes" in overview
        assert "mttr_minutes" in overview
        assert "alert_to_incident_ratio" in overview
        assert "mttd_status" in overview
        assert "mttr_status" in overview
        if overview["mttd_minutes"] is not None:
            assert overview["mttd_minutes"] >= 0.0
        if overview["mttr_minutes"] is not None:
            assert overview["mttr_minutes"] >= 0.0
        assert overview["alert_to_incident_ratio"] >= 0.0


@pytest.mark.asyncio
async def test_analyst_workload_distribution():
    """Verify analyst workload distribution calculates without error."""
    async with AsyncSessionFactory() as db:
        workload = await SOCMetricsService.get_analyst_workload(db)
        assert "total_executions" in workload
        assert "distribution_by_analyst" in workload
