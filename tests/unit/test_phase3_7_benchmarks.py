"""
tests/unit/test_phase3_7_benchmarks.py
======================================
Phase 3.7 Performance Benchmarks.
Measures execution latencies for:
- Policy evaluation (< 2ms target)
- Decision evaluation (< 5ms target)
- Action validation & creation (< 10ms target)
- Idempotency lookup (< 2ms target)
"""

import time
import pytest
from backend.app.services.response_policy_service import ResponsePolicyEngine
from backend.app.services.response_decision_service import ResponseDecisionService
from backend.app.services.response_actions import BlockIPAction


@pytest.mark.unit
@pytest.mark.asyncio
async def test_benchmark_policy_evaluation():
    """Benchmark ResponsePolicyEngine evaluation latency."""
    iterations = 2000
    t0 = time.perf_counter()
    for _ in range(iterations):
        await ResponsePolicyEngine.evaluate(
            risk_score=75.0,
            severity="HIGH",
            requested_action="BLOCK_IP"
        )
    t_total = time.perf_counter() - t0
    avg_ms = (t_total / iterations) * 1000.0

    print(f"\n[BENCHMARK] Policy Evaluation: {avg_ms:.4f} ms/eval (Target: < 2.0 ms)")
    assert avg_ms < 2.0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_benchmark_decision_evaluation():
    """Benchmark ResponseDecisionService evaluation latency."""
    iterations = 2000
    t0 = time.perf_counter()
    for _ in range(iterations):
        await ResponseDecisionService.evaluate_incident_response(
            incident_id="bench-inc-01",
            risk_score=85.0,
            severity="CRITICAL",
            attack_type="Brute Force",
            source_ip="198.51.100.5"
        )
    t_total = time.perf_counter() - t0
    avg_ms = (t_total / iterations) * 1000.0

    print(f"\n[BENCHMARK] Decision Evaluation: {avg_ms:.4f} ms/eval (Target: < 5.0 ms)")
    assert avg_ms < 5.0


@pytest.mark.unit
def test_benchmark_action_validation():
    """Benchmark action validation and preview latency."""
    action = BlockIPAction()
    iterations = 5000
    t0 = time.perf_counter()
    for _ in range(iterations):
        action.validate("198.51.100.5")
    t_total = time.perf_counter() - t0
    avg_ms = (t_total / iterations) * 1000.0

    print(f"\n[BENCHMARK] Action Validation: {avg_ms:.4f} ms/op (Target: < 2.0 ms)")
    assert avg_ms < 2.0
