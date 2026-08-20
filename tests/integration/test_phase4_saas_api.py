"""
tests/integration/test_phase4_saas_api.py
=========================================
Phase 4 Integration Tests: SaaS Management Endpoints (Organizations, Subscriptions, API Keys).
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_saas_metrics_endpoint_publicly_available():
    """Prometheus /metrics scrape endpoint must return 200."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/metrics")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_unauthenticated_organization_access_blocked():
    """Unauthenticated requests to /api/v1/organizations must be rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/organizations/me")
        assert response.status_code in [401, 403]
