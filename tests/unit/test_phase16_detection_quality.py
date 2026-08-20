"""
tests/unit/test_phase16_detection_quality.py
============================================
Phase 16.1 & 16.10 Unit Tests: Detection Quality Engine & Reproducible Benchmarks.
"""

import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.detection_quality_service import DetectionQualityService


@pytest.mark.asyncio
async def test_compute_detection_quality_metrics():
    """Validates precision, recall, F1, FPR, and MTTD/MTTR computation."""
    await init_db()
    async with AsyncSessionFactory() as db:
        metrics = await DetectionQualityService.compute_quality_metrics(
            db=db,
            tenant_id="test-tenant-p16",
            lookback_days=30
        )

        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert "false_positive_rate" in metrics
        assert "mttd_seconds" in metrics
        assert "mttr_seconds" in metrics

        assert 0.0 <= metrics["precision"] <= 1.0
        assert 0.0 <= metrics["recall"] <= 1.0
        assert 0.0 <= metrics["f1_score"] <= 1.0
        assert 0.0 <= metrics["false_positive_rate"] <= 1.0
        assert metrics["mttd_seconds"] > 0
        assert metrics["mttr_seconds"] > 0


@pytest.mark.asyncio
async def test_record_and_get_quality_history():
    """Validates historical snapshot recording and chronological retrieval."""
    await init_db()
    async with AsyncSessionFactory() as db:
        snap = await DetectionQualityService.record_quality_snapshot(
            db=db,
            tenant_id="test-tenant-history"
        )
        assert snap.id is not None
        assert snap.precision > 0.5

        history = await DetectionQualityService.get_quality_history(
            db=db,
            tenant_id="test-tenant-history",
            limit=10
        )
        assert len(history) >= 1
        assert history[0]["precision"] > 0.5


@pytest.mark.asyncio
async def test_reproducible_benchmark_recording():
    """Validates cryptographic SHA-256 result hashing for reproducible ML benchmarks."""
    await init_db()
    async with AsyncSessionFactory() as db:
        benchmark = await DetectionQualityService.record_benchmark(
            db=db,
            dataset="CICIDS2017-Full",
            dataset_version="v2.1",
            model_version="catboost-v1.0",
            throughput_eps=14850.0,
            p50_latency_ms=1.85,
            p95_latency_ms=4.20,
            p99_latency_ms=8.50,
            memory_mb=340.0,
            cpu_percent=18.5,
            hardware_env="Test-Runner-8Core"
        )

        assert benchmark.id is not None
        assert len(benchmark.result_hash) == 64 # SHA-256 hex digest
        assert benchmark.throughput_eps == 14850.0

        b_list = await DetectionQualityService.list_benchmarks(db, limit=5)
        assert len(b_list) >= 1
