"""
tests/integration/test_observability_metrics.py
==============================================
Integration tests for Prometheus metrics exposition, health probes, and streaming observability.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_prometheus_metrics_endpoint():
    """Verify GET /api/v1/metrics/prometheus returns standard exposition format."""
    res = client.get("/api/v1/metrics/prometheus")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    text = res.text
    assert "sentinel_uptime_seconds" in text
    assert "sentinel_database_healthy" in text
    assert "sentinel_stream_ingested_total" in text
    assert "sentinel_stream_dlq_depth" in text


def test_liveness_and_readiness_probes():
    """Verify /health/live and /health/ready probes."""
    live_res = client.get("/health/live")
    assert live_res.status_code == 200
    assert live_res.json()["status"] == "HEALTHY"

    ready_res = client.get("/health/ready")
    assert ready_res.status_code == 200
    data = ready_res.json()
    assert data["ready"] is True
    assert data["database_connected"] is True
    assert data["artifact_integrity"] is True
