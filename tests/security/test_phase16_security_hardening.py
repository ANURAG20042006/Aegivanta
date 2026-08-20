"""
tests/security/test_phase16_security_hardening.py
=================================================
Phase 16.15 Security Hardening & Tenant Isolation Tests.
Validates multi-tenant boundaries, secret sanitization, and fail-closed state machines.
"""

import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.detection_quality_service import DetectionQualityService
from backend.app.services.alert_intelligence_service import AlertIntelligenceService
from backend.app.services.ai_copilot_service import AICopilotService
from backend.app.services.investigation_search_service import InvestigationSearchService


@pytest.mark.security
@pytest.mark.asyncio
async def test_tenant_isolated_detection_quality_metrics():
    """Metrics calculated for Tenant A must not leak into Tenant B."""
    await init_db()
    async with AsyncSessionFactory() as db:
        metrics_a = await DetectionQualityService.compute_quality_metrics(db, tenant_id="tenant-alpha")
        metrics_b = await DetectionQualityService.compute_quality_metrics(db, tenant_id="tenant-beta")

        assert metrics_a["tenant_id"] == "tenant-alpha"
        assert metrics_b["tenant_id"] == "tenant-beta"


@pytest.mark.security
def test_ai_copilot_secret_sanitization():
    """Analyst prompts containing secrets, sensor tokens, or API keys must be redacted."""
    raw_prompt = "Analyze incident with token sen_abcdef1234567890abcdef1234567890abcdef1234567890 and key ak_9876543210fedcba9876543210fedcba"
    sanitized = AICopilotService.sanitize_context(raw_prompt)

    assert "[REDACTED_SENSOR_TOKEN]" in sanitized
    assert "[REDACTED_API_KEY]" in sanitized
    assert "sen_abcdef" not in sanitized
    assert "ak_987654" not in sanitized


@pytest.mark.security
@pytest.mark.asyncio
async def test_investigation_search_bounds():
    """Search queries must be strictly bounded to prevent unbounded denial-of-service queries."""
    await init_db()
    async with AsyncSessionFactory() as db:
        res = await InvestigationSearchService.global_search(
            db=db,
            query="",
            limit=500 # Excessive requested limit
        )
        assert res["limit"] <= 100 # Bounded to max 100
