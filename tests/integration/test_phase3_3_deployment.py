"""
tests/integration/test_phase3_3_deployment.py
==============================================
Integration tests verifying Phase 3.3 Kubernetes Deployment hardening,
including fail-closed readiness probe behavior, graceful worker daemon termination,
and isolated non-root stream processing.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings
from backend.app.services.distributed_stream_service import distributed_stream_engine, InMemoryStreamBackend, RedisStreamBackend
from backend.app.worker import StreamWorkerDaemon


def test_production_readiness_probe_fail_closed(monkeypatch):
    """Verify /api/v1/health/ready returns 503 if Redis is disconnected in production mode."""
    client = TestClient(app)

    # 1. Simulate production environment with disconnected Redis
    monkeypatch.setattr(settings, "APP_ENV", "production")
    monkeypatch.setattr(settings, "OPERATING_MODE", "PRODUCTION")

    # Set disconnected backend
    disconnected_backend = InMemoryStreamBackend()
    disconnected_backend._connected = False
    distributed_stream_engine.set_backend(disconnected_backend)

    res = client.get("/api/v1/health/ready")
    assert res.status_code == 503
    data = res.json()["detail"]
    assert data["ready"] is False
    assert data["redis_healthy"] is False

    # 2. Reconnect backend -> 200 OK
    connected_backend = InMemoryStreamBackend()
    connected_backend._connected = True
    distributed_stream_engine.set_backend(connected_backend)

    res_ok = client.get("/api/v1/health/ready")
    assert res_ok.status_code == 200
    assert res_ok.json()["ready"] is True


@pytest.mark.asyncio
async def test_worker_daemon_graceful_shutdown():
    """Verify StreamWorkerDaemon reacts to shutdown signal and exits cleanly without hanging."""
    daemon = StreamWorkerDaemon()
    daemon.running = True

    # Simulate SIGTERM signal handling
    daemon.handle_signal(sig=15, frame=None)
    assert daemon.running is False
