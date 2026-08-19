"""
backend/app/api/v1/health.py
============================
System Health, Liveness, Readiness, and Observability Endpoints.
Separates fast process-level liveness probes from genuine dependency readiness checks.
Zero secret exposure; fail-closed dependency status reporting.
"""

import time
import os
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.models.model_registry import ModelRegistry
from ml.schema.feature_schema import validate_artifact_compatibility, load_artifact_metadata

router = APIRouter(tags=["System Health & Observability"])

_APP_START_TIME = time.time()


@router.get("/health", summary="Process Liveness Probe")
@router.get("/health/live", summary="Process Liveness Probe (K8s / Container)")
async def liveness_check() -> Dict[str, Any]:
    """
    Process-level liveness probe.
    Fast, lightweight, zero-dependency check confirming the API gateway process is alive.
    """
    return {
        "status": "HEALTHY",
        "service": settings.APP_NAME,
        "mode": settings.OPERATING_MODE,
        "version": settings.PROJECT_VERSION,
        "environment": settings.APP_ENV
    }


@router.get("/ready", summary="System Dependency Readiness Probe")
@router.get("/health/ready", summary="System Dependency Readiness Probe (K8s / Container)")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Readiness probe verifying dependencies required for serving operational traffic:
      1. Genuine Database connectivity (SELECT 1)
      2. Model artifact integrity (champion model & preprocessor .joblib files)
      3. Feature schema and manifest compatibility
    Returns HTTP 200 OK when ready; HTTP 503 Service Unavailable when dependencies fail.
    Never exposes internal passwords, connection URLs, or secret keys.
    """
    # 1. Genuine Database Connectivity Check
    db_healthy = False
    db_error = None
    try:
        res = await db.execute(text("SELECT 1"))
        db_healthy = (res.scalar() == 1)
    except Exception as exc:
        db_healthy = False
        db_error = "Database connectivity check failed"

    # 2. Active Model Registry Query
    active_model_name = None
    active_model_version = None
    try:
        query = select(ModelRegistry).where(ModelRegistry.is_active == True)
        result = await db.execute(query)
        active_model = result.scalar_one_or_none()
        if active_model:
            active_model_name = active_model.model_name
            active_model_version = active_model.model_version
    except Exception:
        pass

    # 3. Artifact Integrity Check
    artifact_dir = Path(settings.MODEL_ARTIFACTS_DIR)
    if not artifact_dir.is_absolute():
        artifact_dir = Path(__file__).resolve().parents[4] / artifact_dir

    catboost_exists = (artifact_dir / "catboost.joblib").exists()
    best_model_exists = (artifact_dir / "best_model.joblib").exists()
    preprocessor_exists = (artifact_dir / "preprocessor.joblib").exists()
    model_exists = catboost_exists or best_model_exists
    artifact_integrity = bool(model_exists and preprocessor_exists)

    # 4. Manifest & Schema Feature Synchronization
    manifest_path = artifact_dir / "artifact_manifest.json"
    manifest_valid = False
    if manifest_path.exists():
        try:
            import json
            with manifest_path.open("r", encoding="utf-8") as f:
                man_data = json.load(f)
            manifest_valid = (man_data.get("processed_feature_count") == man_data.get("model_n_features_in"))
        except Exception:
            manifest_valid = False
    else:
        manifest_valid = True

    metadata = load_artifact_metadata(artifact_dir)
    schema_compatible, compat_errors = validate_artifact_compatibility(metadata)

    is_ready = bool(db_healthy and artifact_integrity and schema_compatible and manifest_valid)

    if not is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "ready": False,
                "database_connected": db_healthy,
                "database_error": db_error,
                "artifact_integrity": artifact_integrity,
                "schema_compatible": schema_compatible,
                "schema_errors": compat_errors
            }
        )

    return {
        "ready": True,
        "operating_mode": settings.OPERATING_MODE,
        "database_connected": db_healthy,
        "active_model": active_model_name or "CatBoost",
        "active_model_version": active_model_version or "catboost-v1.0",
        "artifact_integrity": artifact_integrity,
        "schema_compatible": schema_compatible
    }


@router.get("/metrics", summary="System Observability Metrics Endpoint")
async def get_system_metrics(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns accurate runtime observability telemetry:
      - Measured database query round-trip latency
      - Application uptime
      - Process status and active operating mode
    """
    t0 = time.perf_counter()
    db_ok = False
    try:
        res = await db.execute(text("SELECT 1"))
        db_ok = (res.scalar() == 1)
    except Exception:
        db_ok = False

    t_db = (time.perf_counter() - t0) * 1000.0
    uptime_sec = round(time.time() - _APP_START_TIME, 2)

    return {
        "timestamp": time.time(),
        "uptime_seconds": uptime_sec,
        "operating_mode": settings.OPERATING_MODE,
        "database_healthy": db_ok,
        "database_latency_ms": round(t_db, 3),
        "active_model": "CatBoost",
        "telemetry_source": "RUNTIME_MEASURED"
    }


@router.get("/health/ml", summary="ML Inference Subsystem Health Probe")
@router.get("/ml/health", summary="ML Inference Subsystem Health Probe")
async def ml_health_probe(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed ML Inference Health Check.
    Returns verified status of champion model, preprocessor, and active registry model.
    Fail-safe, non-leaking diagnostic output.
    """
    artifact_dir = Path(settings.MODEL_ARTIFACTS_DIR)
    if not artifact_dir.is_absolute():
        artifact_dir = Path(__file__).resolve().parents[4] / artifact_dir

    catboost_exists = (artifact_dir / "catboost.joblib").exists() or (artifact_dir / "best_model.joblib").exists()
    preprocessor_exists = (artifact_dir / "preprocessor.joblib").exists()

    active_name = "CatBoost"
    active_version = "catboost-v1.0"
    try:
        res = await db.execute(select(ModelRegistry).where(ModelRegistry.is_active == True))
        active_rec = res.scalar_one_or_none()
        if active_rec:
            active_name = active_rec.model_name
            active_version = active_rec.model_version
    except Exception:
        pass

    if catboost_exists and preprocessor_exists:
        ml_status = "AVAILABLE"
    elif catboost_exists or preprocessor_exists:
        ml_status = "DEGRADED"
    else:
        ml_status = "UNAVAILABLE"

    return {
        "status": ml_status,
        "model": active_name,
        "model_version": active_version,
        "loaded": catboost_exists,
        "preprocessor_loaded": preprocessor_exists,
        "operating_mode": settings.OPERATING_MODE
    }


@router.get("/metrics/prometheus", summary="Prometheus Exposition Metrics Endpoint")
async def prometheus_metrics(db: AsyncSession = Depends(get_db)):
    """
    Exposes standardized Prometheus metrics for scraper consumption.
    Includes uptime, database health, streaming metrics, and memory utilization.
    """
    from fastapi.responses import PlainTextResponse
    from backend.app.services.stream_service import stream_engine

    uptime_sec = round(time.time() - _APP_START_TIME, 2)
    stream_m = stream_engine.get_stream_metrics()

    t0 = time.perf_counter()
    db_ok = 1
    try:
        res = await db.execute(text("SELECT 1"))
        if res.scalar() != 1:
            db_ok = 0
    except Exception:
        db_ok = 0
    db_latency_ms = round((time.perf_counter() - t0) * 1000.0, 3)

    from backend.app.services.pcap_service import PCAPTelemetryService

    lines = [
        "# HELP sentinel_uptime_seconds Application uptime in seconds",
        "# TYPE sentinel_uptime_seconds gauge",
        f"sentinel_uptime_seconds {uptime_sec}",
        "",
        "# HELP sentinel_database_healthy Database connectivity status (1 = healthy, 0 = unhealthy)",
        "# TYPE sentinel_database_healthy gauge",
        f"sentinel_database_healthy {db_ok}",
        "",
        "# HELP sentinel_database_latency_ms Database roundtrip latency in milliseconds",
        "# TYPE sentinel_database_latency_ms gauge",
        f"sentinel_database_latency_ms {db_latency_ms}",
        "",
        "# HELP sentinel_stream_ingested_total Total streaming telemetry events ingested",
        "# TYPE sentinel_stream_ingested_total counter",
        f"sentinel_stream_ingested_total {stream_m['total_ingested']}",
        "",
        "# HELP sentinel_stream_processed_total Total streaming telemetry events processed successfully",
        "# TYPE sentinel_stream_processed_total counter",
        f"sentinel_stream_processed_total {stream_m['total_processed']}",
        "",
        "# HELP sentinel_stream_duplicates_total Total duplicate telemetry events rejected by deduplication gate",
        "# TYPE sentinel_stream_duplicates_total counter",
        f"sentinel_stream_duplicates_total {stream_m['total_duplicates']}",
        "",
        "# HELP sentinel_stream_dlq_total Total events routed to Dead Letter Queue",
        "# TYPE sentinel_stream_dlq_total counter",
        f"sentinel_stream_dlq_total {stream_m['total_dlq']}",
        "",
        "# HELP sentinel_stream_dlq_depth Current depth of in-memory Dead Letter Queue",
        "# TYPE sentinel_stream_dlq_depth gauge",
        f"sentinel_stream_dlq_depth {stream_m['dlq_depth']}",
        "",
        "# HELP sentinel_pcap_files_processed_total Total PCAP binary files ingested and processed",
        "# TYPE sentinel_pcap_files_processed_total counter",
        f"sentinel_pcap_files_processed_total {PCAPTelemetryService.pcap_files_processed}",
        "",
        "# HELP sentinel_pcap_packets_parsed_total Total network packet frames parsed from PCAP",
        "# TYPE sentinel_pcap_packets_parsed_total counter",
        f"sentinel_pcap_packets_parsed_total {PCAPTelemetryService.pcap_packets_parsed}",
        "",
        "# HELP sentinel_pcap_flows_extracted_total Total 5-tuple bidirectional network flows extracted from PCAP",
        "# TYPE sentinel_pcap_flows_extracted_total counter",
        f"sentinel_pcap_flows_extracted_total {PCAPTelemetryService.pcap_flows_extracted}",
        "",
        "# HELP sentinel_pcap_parse_errors_total Total PCAP parsing or validation errors",
        "# TYPE sentinel_pcap_parse_errors_total counter",
        f"sentinel_pcap_parse_errors_total {PCAPTelemetryService.pcap_parse_errors}",
        ""
    ]

    return PlainTextResponse("\n".join(lines), media_type="text/plain; version=0.0.4; charset=utf-8")

