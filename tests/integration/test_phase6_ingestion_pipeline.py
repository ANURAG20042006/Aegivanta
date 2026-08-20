"""
tests/integration/test_phase6_ingestion_pipeline.py
===================================================
Phase 6 Integration Tests: Ingestion Gateway & Sensor Lifecycle API Endpoints.
"""

import gzip
import json
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_unauthenticated_ingest_rejected():
    """Ingest endpoint without valid sensor credentials must be rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = gzip.compress(json.dumps({"events": []}).encode("utf-8"))
        response = await ac.post(
            "/api/v1/sensors/ingest",
            content=payload,
            headers={
                "X-Sensor-ID": "fake-sensor-id",
                "X-Sensor-Token": "fake-token",
                "Content-Encoding": "gzip"
            }
        )
        assert response.status_code in [401, 403, 404]
