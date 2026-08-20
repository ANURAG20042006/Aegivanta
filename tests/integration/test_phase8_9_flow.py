"""
tests/integration/test_phase8_9_flow.py
=======================================
Integration tests for Detection-as-Code Sandbox & AI Copilot Router Endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_unauthenticated_detection_rule_test_rejected():
    """Unauthenticated requests to /api/v1/detection-rules/test must be rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "rule_dsl": {"field": "data.protocol", "op": "eq", "value": "TCP"},
            "sample_events": [
                {"data": {"protocol": "TCP"}},
                {"data": {"protocol": "UDP"}}
            ]
        }
        response = await ac.post("/api/v1/detection-rules/test", json=payload)
        assert response.status_code in [401, 403]



@pytest.mark.asyncio
async def test_unauthenticated_copilot_query():
    """Unauthenticated call to /copilot/query must be rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/copilot/query", json={"query": "hello"})
        assert response.status_code in [400, 401, 403]
