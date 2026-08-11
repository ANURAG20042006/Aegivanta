from pathlib import Path
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.config import settings

router = APIRouter(tags=["System Health & Observability"])


@router.get("/health", summary="Basic System Health Check")
async def health_check():
    """Basic health check endpoint returning API service status."""
    return {
        "status": "HEALTHY",
        "service": "SentinelAI NIDS API Gateway",
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT
    }


@router.get("/ready", summary="Readiness & ML Artifact Integrity Check")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Deep readiness check verifying Database connectivity and Model Artifact integrity."""
    db_healthy = False
    try:
        res = await db.execute(text("SELECT 1"))
        db_healthy = (res.scalar() == 1)
    except Exception:
        db_healthy = False

    artifact_dir = Path(settings.MODEL_ARTIFACTS_DIR)
    if not artifact_dir.is_absolute():
        artifact_dir = Path(__file__).resolve().parents[3] / artifact_dir

    artifacts_exist = (artifact_dir / "preprocessor.joblib").exists() and (artifact_dir / "best_model.joblib").exists()

    is_ready = db_healthy and artifacts_exist

    return {
        "ready": is_ready,
        "database_connected": db_healthy,
        "ml_artifacts_present": artifacts_exist,
        "model_artifacts_directory": str(artifact_dir)
    }
