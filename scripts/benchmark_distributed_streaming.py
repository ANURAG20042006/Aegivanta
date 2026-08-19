"""
scripts/benchmark_distributed_streaming.py
==========================================
Empirical Performance Benchmark for SentinelAI Phase 3.2 Distributed Streaming Infrastructure.
Measures Redis Stream publish, consumer group XREADGROUP, XACK, atomic idempotency SET NX,
DLQ insertion, and Pub/Sub broadcast latencies.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import asyncio
import platform
import numpy as np
import fakeredis.aioredis

from backend.app.services.distributed_stream_service import RedisStreamBackend, DistributedStreamEngine


async def run_benchmark():
    python_ver = sys.version.split()[0]
    os_name = platform.platform()
    proc = platform.processor() or "x86_64"

    fake_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    backend = RedisStreamBackend()
    backend._client = fake_client
    backend._connected = True
    engine = DistributedStreamEngine(backend=backend)

    WARMUP_RUNS = 10
    BENCHMARK_RUNS = 100

    print("=================================================================")
    print("  SentinelAI Phase 3.2 Distributed Streaming Benchmark           ")
    print("=================================================================")
    print(f"OS/Platform       : {os_name}")
    print(f"Processor/CPU     : {proc}")
    print(f"Python Version    : {python_ver}")
    print(f"Redis Engine      : Redis Streams (fakeredis-aioredis protocol engine)")
    print(f"Benchmark Config  : {BENCHMARK_RUNS} iterations ({WARMUP_RUNS} warmups)")
    print("-----------------------------------------------------------------")

    # 1. Benchmark Stream Publish
    stream_key = "benchmark:stream"
    for _ in range(WARMUP_RUNS):
        await backend.publish_event(stream_key, {"event_id": "warmup", "src": "10.0.0.1"})

    pub_times = []
    for i in range(BENCHMARK_RUNS):
        t0 = time.perf_counter()
        await backend.publish_event(stream_key, {"event_id": f"evt-{i}", "src": f"192.168.1.{i%250}"})
        pub_times.append((time.perf_counter() - t0) * 1000.0)

    # 2. Benchmark Consumer Group Read (XREADGROUP)
    group_key = "benchmark:group"
    for _ in range(WARMUP_RUNS):
        await backend.consume_events(stream_key, group_key, "bench-worker", count=5, block_ms=10)

    read_times = []
    msg_ids_to_ack = []
    for _ in range(BENCHMARK_RUNS):
        t0 = time.perf_counter()
        msgs = await backend.consume_events(stream_key, group_key, "bench-worker", count=1, block_ms=10)
        read_times.append((time.perf_counter() - t0) * 1000.0)
        if msgs:
            msg_ids_to_ack.append(msgs[0]["id"])

    # 3. Benchmark Message ACK (XACK)
    ack_times = []
    for msg_id in msg_ids_to_ack[:BENCHMARK_RUNS]:
        t0 = time.perf_counter()
        await backend.acknowledge_event(stream_key, group_key, msg_id)
        ack_times.append((time.perf_counter() - t0) * 1000.0)

    # 4. Benchmark Atomic Check-and-Set Idempotency (SET NX EX)
    idemp_times = []
    for i in range(BENCHMARK_RUNS):
        key = f"bench-hash-{i}-{time.time()}"
        t0 = time.perf_counter()
        await backend.check_and_set_idempotency(key, ttl_seconds=3600)
        idemp_times.append((time.perf_counter() - t0) * 1000.0)

    # 5. Benchmark Durable DLQ Insertion
    dlq_times = []
    for i in range(BENCHMARK_RUNS):
        t0 = time.perf_counter()
        await backend.push_to_dlq(
            "benchmark:dlq",
            {"event_id": f"dlq-{i}", "reason": "simulated"},
            reason="Benchmark DLQ push",
            attempts=3,
            source_worker="bench-worker"
        )
        dlq_times.append((time.perf_counter() - t0) * 1000.0)

    # 6. Benchmark Redis Pub/Sub Broadcast
    pubsub_times = []
    for i in range(BENCHMARK_RUNS):
        t0 = time.perf_counter()
        await backend.publish_pubsub("benchmark:events", {"type": "TEST", "index": i})
        pubsub_times.append((time.perf_counter() - t0) * 1000.0)

    def print_stat(label: str, arr: list):
        print(f"{label:<38}: Mean={np.mean(arr):.3f}ms | p50={np.percentile(arr, 50):.3f}ms | p95={np.percentile(arr, 95):.3f}ms | p99={np.percentile(arr, 99):.3f}ms")

    print_stat("1. Stream Event Publish (XADD)", pub_times)
    print_stat("2. Consumer Group Read (XREADGROUP)", read_times)
    print_stat("3. Message Acknowledgment (XACK)", ack_times)
    print_stat("4. Atomic Idempotency (SET NX EX)", idemp_times)
    print_stat("5. Durable DLQ Persistence", dlq_times)
    print_stat("6. Redis Pub/Sub Broadcast", pubsub_times)
    print("=================================================================")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
