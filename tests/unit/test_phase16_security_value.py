"""
tests/unit/test_phase16_security_value.py
=========================================
Phase 16.8, 16.9, 16.11 & 16.12 Unit Tests: Security Value, Posture, Costs & Product Analytics.
"""

import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.security_value_service import SecurityValueService


@pytest.mark.asyncio
async def test_get_security_value_metrics():
    """Validates cybersecurity ROI calculations, threats blocked, and trends."""
    await init_db()
    async with AsyncSessionFactory() as db:
        res = await SecurityValueService.get_security_value_metrics(
            db=db,
            tenant_id="test-val-tenant",
            lookback_days=30
        )
        assert "threats_detected" in res
        assert "threats_blocked" in res
        assert "risk_reduction_percentage" in res
        assert "trends" in res
        assert "7_days" in res["trends"]


@pytest.mark.asyncio
async def test_get_posture_improvements():
    """Validates explainable security score improvements with estimated impact points."""
    await init_db()
    async with AsyncSessionFactory() as db:
        res = await SecurityValueService.get_posture_improvements(
            db=db,
            tenant_id="test-posture-tenant"
        )
        assert "current_score" in res
        assert "potential_score" in res
        assert "recommendations" in res
        assert len(res["recommendations"]) >= 1
        for rec in res["recommendations"]:
            assert rec["estimated_impact_points"] > 0
            assert "category" in rec


@pytest.mark.asyncio
async def test_get_telemetry_cost_intelligence():
    """Validates telemetry volume, duplicate tracking, and cost optimization tips."""
    await init_db()
    async with AsyncSessionFactory() as db:
        res = await SecurityValueService.get_telemetry_cost_intelligence(
            db=db,
            tenant_id="test-cost-tenant"
        )
        assert "daily_events_estimated" in res
        assert "monthly_bytes_estimated" in res
        assert "optimization_recommendations" in res
        assert len(res["optimization_recommendations"]) >= 1


@pytest.mark.asyncio
async def test_get_product_analytics():
    """Validates privacy-conscious administrative platform metrics."""
    await init_db()
    async with AsyncSessionFactory() as db:
        res = await SecurityValueService.get_product_analytics(db=db)
        assert res["platform_version"] == "v16.0.0"
        assert "features_enabled" in res
        assert len(res["features_enabled"]) >= 5
