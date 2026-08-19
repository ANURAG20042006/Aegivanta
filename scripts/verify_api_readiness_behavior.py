"""
scripts/verify_api_readiness_behavior.py
========================================
Validates API readiness behavior under online vs offline Redis states
in production vs development modes.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings
from backend.app.services.distributed_stream_service import distributed_stream_engine, InMemoryStreamBackend


def verify_readiness():
    client = TestClient(app)

    print("=================================================================")
    print("      SentinelAI Live API Readiness & Fail-Closed Validation     ")
    print("=================================================================")

    # Test 1: Production Mode with Redis Online
    settings.APP_ENV = "production"
    settings.OPERATING_MODE = "PRODUCTION"
    backend_online = InMemoryStreamBackend()
    backend_online._connected = True
    distributed_stream_engine.set_backend(backend_online)

    res1 = client.get("/api/v1/health/ready")
    print(f"Scenario 1: [PRODUCTION + REDIS ONLINE]")
    print(f"  HTTP Status : {res1.status_code}")
    print(f"  Response Body: {res1.json()}")
    assert res1.status_code == 200
    assert res1.json()["ready"] is True
    assert res1.json()["redis_connected"] is True
    print("  -> PASS: Successfully returned HTTP 200 with ready=True and redis_connected=True\n")

    # Test 2: Production Mode with Redis Offline (Fail-Closed)
    backend_offline = InMemoryStreamBackend()
    backend_offline._connected = False
    distributed_stream_engine.set_backend(backend_offline)

    res2 = client.get("/api/v1/health/ready")
    print(f"Scenario 2: [PRODUCTION + REDIS OFFLINE (FAIL-CLOSED)]")
    print(f"  HTTP Status : {res2.status_code}")
    print(f"  Response Body: {res2.json()}")
    assert res2.status_code == 503
    assert res2.json()["detail"]["ready"] is False
    assert res2.json()["detail"]["redis_healthy"] is False
    print("  -> PASS: Successfully failed closed with HTTP 503 and ready=False\n")

    # Test 3: Restored Redis Online in Production
    backend_restored = InMemoryStreamBackend()
    backend_restored._connected = True
    distributed_stream_engine.set_backend(backend_restored)

    res3 = client.get("/api/v1/health/ready")
    print(f"Scenario 3: [PRODUCTION + REDIS RESTORED]")
    print(f"  HTTP Status : {res3.status_code}")
    print(f"  Response Body: {res3.json()}")
    assert res3.status_code == 200
    assert res3.json()["ready"] is True
    assert res3.json()["redis_connected"] is True
    print("  -> PASS: Readiness cleanly recovered to HTTP 200\n")

    # Reset back to development
    settings.APP_ENV = "development"
    settings.OPERATING_MODE = "DEMO"
    print("=================================================================")
    print("RESULT: ALL 3 READINESS SCENARIOS VERIFIED CLEANLY")
    print("=================================================================")


if __name__ == "__main__":
    verify_readiness()
