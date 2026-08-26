from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext, get_enforced_tenant_id
from backend.app.services.detection_quality_service import DetectionQualityService
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/detection", tags=["Detection Quality & Benchmarking"])


@router.get("/quality", summary="Get Current Tenant Detection Quality Metrics")
async def get_detection_quality(
    lookback_days: int = Query(30, ge=1, le=365),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates precision, recall, F1, FPR, MTTD, MTTA, and MTTR for the active tenant."""
    tenant_id = get_enforced_tenant_id(context)
    return await DetectionQualityService.compute_quality_metrics(db, tenant_id, lookback_days)


@router.get("/quality/history", summary="Get Historical Detection Quality Snapshots")
async def get_quality_history(
    limit: int = Query(30, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Returns chronologically ordered historical quality snapshots for trend charts."""
    tenant_id = get_enforced_tenant_id(context)
    return await DetectionQualityService.get_quality_history(db, tenant_id, limit)


@router.get("/benchmarks", summary="List Reproducible Detection Benchmarks")
async def list_benchmarks(
    limit: int = Query(20, ge=1, le=50),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists reproducible model benchmarks with latency percentiles and cryptographic result hashes."""
    benchmarks = await DetectionQualityService.list_benchmarks(db, limit)
    return [
        {
            "id": b.id,
            "dataset": b.dataset,
            "dataset_version": b.dataset_version,
            "model_version": b.model_version,
            "throughput_eps": b.throughput_eps,
            "p50_latency_ms": b.p50_latency_ms,
            "p95_latency_ms": b.p95_latency_ms,
            "p99_latency_ms": b.p99_latency_ms,
            "memory_mb": b.memory_mb,
            "cpu_percent": b.cpu_percent,
            "hardware_environment": b.hardware_environment,
            "result_hash": b.result_hash,
            "timestamp": b.timestamp.isoformat()
        }
        for b in benchmarks
    ]
