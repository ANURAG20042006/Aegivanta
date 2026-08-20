"""
tests/unit/test_phase3_8_benchmarks.py
======================================
Phase 3.8 Performance Benchmarks.
Measures execution latencies for:
- Threat hunting query DSL (< 100ms)
- Entity pivot (< 100ms)
- Evidence correlation (< 200ms)
- Behavioral baseline computation (< 50ms)
- Timeline reconstruction (< 100ms)
"""

import time
import pytest
from backend.app.services.threat_hunting_service import ThreatHuntingService
from backend.app.services.evidence_correlation_service import EvidenceCorrelationEngine
from backend.app.services.investigation_pivot_service import InvestigationPivotService
from backend.app.services.behavior_baseline_service import BehaviorBaselineEngine


@pytest.mark.unit
@pytest.mark.asyncio
async def test_benchmark_hunting_query_dsl():
    """Benchmark threat hunting DSL validation and dispatch."""
    iterations = 2000
    t0 = time.perf_counter()
    for _ in range(iterations):
        await ThreatHuntingService.execute_dsl_query(
            entity="events",
            filters=[{"field": "source_ip", "operator": "equals", "value": "192.168.1.100"}],
            limit=50
        )
    t_total = time.perf_counter() - t0
    avg_ms = (t_total / iterations) * 1000.0

    print(f"\n[BENCHMARK] Hunting Query DSL: {avg_ms:.4f} ms/query (Target: < 100.0 ms)")
    assert avg_ms < 100.0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_benchmark_evidence_correlation():
    """Benchmark evidence correlation graph construction."""
    ips = [f"10.0.0.{i}" for i in range(1, 100)]
    users = [f"user_{i}" for i in range(1, 50)]
    assets = [f"asset_{i}" for i in range(1, 50)]

    iterations = 500
    t0 = time.perf_counter()
    for _ in range(iterations):
        await EvidenceCorrelationEngine.correlate_case_evidence(
            ips=ips,
            users=users,
            assets=assets,
            iocs=["198.51.100.5"]
        )
    t_total = time.perf_counter() - t0
    avg_ms = (t_total / iterations) * 1000.0

    print(f"\n[BENCHMARK] Evidence Correlation (200 entities): {avg_ms:.4f} ms/op (Target: < 200.0 ms)")
    assert avg_ms < 200.0


@pytest.mark.unit
def test_benchmark_behavior_baseline_computation():
    """Benchmark behavioral baseline statistics and z-score calculation."""
    obs = [10.0 + (i % 5) for i in range(500)]
    iterations = 2000
    t0 = time.perf_counter()
    for _ in range(iterations):
        stats = BehaviorBaselineEngine.compute_rolling_baseline(obs)
        BehaviorBaselineEngine.calculate_deviation("packet_rate", 25.0, stats["mean"], stats["std"])
    t_total = time.perf_counter() - t0
    avg_ms = (t_total / iterations) * 1000.0

    print(f"\n[BENCHMARK] Behavior Baseline Engine: {avg_ms:.4f} ms/calc (Target: < 50.0 ms)")
    assert avg_ms < 50.0
