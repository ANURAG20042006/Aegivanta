"""
tests/integration/test_phase5_identity_flow.py
==============================================
Phase 5 Integration Tests: Identity & Security Center API Endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_unauthenticated_mfa_setup_rejected():
    """Unauthenticated requests to /api/v1/identity/mfa/setup must be rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/identity/mfa/setup")
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_unauthenticated_security_posture_rejected():
    """Unauthenticated requests to /api/v1/security/posture must be rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/security/posture")
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_unauthenticated_scim_users_rejected():
    """Unauthenticated requests to SCIM /scim/v2/Users must be rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/scim/v2/Users", json={})
        assert response.status_code == 401
