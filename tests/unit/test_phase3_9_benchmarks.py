"""
tests/unit/test_phase3_9_benchmarks.py
======================================
Performance benchmarks for SOC Dashboard Aggregation Engine and Real-Time Event Streaming.
"""

import time
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.soc_dashboard_service import SOCDashboardService
from backend.app.services.soc_event_broadcaster import SOCEventBroadcaster


@pytest.mark.asyncio
async def test_benchmark_dashboard_overview_metrics_latency():
    await init_db()
    async with AsyncSessionFactory() as db:
        # Warmup
        _ = await SOCDashboardService.get_overview_metrics(db=db, lookback_days=30)

        # Benchmark 10 iterations
        t0 = time.perf_counter()
        iterations = 10
        for _ in range(iterations):
            _ = await SOCDashboardService.get_overview_metrics(db=db, lookback_days=30)
        elapsed_total = time.perf_counter() - t0
        avg_latency_ms = (elapsed_total / iterations) * 1000.0

        print(f"\n[BENCHMARK] Average Overview Aggregation Latency: {avg_latency_ms:.4f} ms")
        assert avg_latency_ms < 150.0, f"Overview aggregation exceeded 150ms: {avg_latency_ms:.2f}ms"


@pytest.mark.asyncio
async def test_benchmark_dashboard_incidents_query_latency():
    await init_db()
    async with AsyncSessionFactory() as db:
        # Benchmark paginated incidents query
        t0 = time.perf_counter()
        iterations = 10
        for _ in range(iterations):
            _ = await SOCDashboardService.get_dashboard_incidents(
                db=db,
                page=1,
                limit=25,
                sort_by="risk_score",
                sort_order="desc"
            )
        avg_latency_ms = ((time.perf_counter() - t0) / iterations) * 1000.0

        print(f"\n[BENCHMARK] Average Incidents Query Latency: {avg_latency_ms:.4f} ms")
        assert avg_latency_ms < 100.0, f"Incidents query exceeded 100ms: {avg_latency_ms:.2f}ms"


@pytest.mark.asyncio
async def test_benchmark_event_broadcasting_latency():
    broadcaster = SOCEventBroadcaster(max_buffer_size=500)

    t0 = time.perf_counter()
    iterations = 100
    for i in range(iterations):
        await broadcaster.broadcast_event(
            event_type="NEW_DETECTION",
            title=f"Benchmark Alert #{i}",
            description="High throughput event stream verification",
            severity="MEDIUM",
            publish_to_redis=False
        )
    avg_latency_ms = ((time.perf_counter() - t0) / iterations) * 1000.0

    print(f"\n[BENCHMARK] Average Event Broadcast Latency: {avg_latency_ms:.4f} ms")
    assert avg_latency_ms < 5.0, f"Event broadcast exceeded 5ms: {avg_latency_ms:.2f}ms"
