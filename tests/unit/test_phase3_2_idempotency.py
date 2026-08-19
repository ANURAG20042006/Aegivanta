"""
tests/unit/test_phase3_2_idempotency.py
======================================
Unit tests for Phase 3.2 Cross-Worker Atomic Idempotency.
Verifies atomic check-and-set (SET NX EX) and race-condition deduplication across multiple workers.
"""

import pytest
import asyncio
import fakeredis.aioredis
from backend.app.services.distributed_stream_service import RedisStreamBackend, DistributedStreamEngine


@pytest.mark.asyncio
async def test_atomic_check_and_set_idempotency():
    """Verify first seen event succeeds and subsequent duplicate is atomically rejected."""
    fake_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    backend = RedisStreamBackend()
    backend._client = fake_client
    backend._connected = True

    dedup_key = "hash-sha256-telemetry-flow-abc123"

    # 1. First worker check-and-set -> True (allowed)
    res_1 = await backend.check_and_set_idempotency(dedup_key, ttl_seconds=3600)
    assert res_1 is True

    # 2. Second worker check-and-set with same key -> False (duplicate rejected)
    res_2 = await backend.check_and_set_idempotency(dedup_key, ttl_seconds=3600)
    assert res_2 is False


@pytest.mark.asyncio
async def test_engine_cross_worker_concurrent_ingestion_deduplication():
    """Verify concurrent ingestion of identical telemetry events by multiple workers processes only once."""
    fake_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    backend = RedisStreamBackend()
    backend._client = fake_client
    backend._connected = True

    engine_w1 = DistributedStreamEngine(backend=backend)
    engine_w2 = DistributedStreamEngine(backend=backend)

    telemetry_payload = {
        "source_ip": "198.51.100.99",
        "destination_ip": "10.0.0.1",
        "source_port": 54321,
        "destination_port": 80,
        "protocol": "TCP",
        "flow_duration": 15000.0,
        "total_fwd_packets": 10.0,
        "packet_length_mean": 512.0
    }

    # Simulate concurrent ingestion by two independent workers
    results = await asyncio.gather(
        engine_w1.ingest_event(dict(telemetry_payload)),
        engine_w2.ingest_event(dict(telemetry_payload))
    )

    statuses = [r["status"] for r in results]
    assert "QUEUED" in statuses
    assert "DUPLICATE" in statuses
