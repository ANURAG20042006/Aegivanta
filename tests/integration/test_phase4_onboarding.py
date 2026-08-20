"""
tests/integration/test_phase4_onboarding.py
===========================================
Phase 4 Integration Tests: Customer Guided Onboarding Workflow.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_unauthenticated_onboarding_status_blocked():
    """Unauthenticated requests to /api/v1/onboarding/status must be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/onboarding/status")
        assert response.status_code in [401, 403]
