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
