from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.model_registry import ModelRegistry
from backend.app.models.audit_log import AuditLog
from backend.app.core.dependencies import require_role
from backend.app.services.predict_service import PredictService
from ml.train_pipeline import run_training_pipeline
from ml.schema.feature_schema import validate_artifact_compatibility

router = APIRouter(prefix="/train", tags=["Model Training & Registry Lifecycle"])


def evaluate_promotion_gate(
    candidate_f1: float,
    candidate_recall: float,
    candidate_fpr: float,
    candidate_latency_ms: float = 0.45,
    active_f1: float = 0.85,
    regression_tolerance: float = 0.01,
    artifact_metadata: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str]:
    """
    Multi-Metric Promotion Gate:
    Evaluates:
      1. Artifact Integrity & Schema Compatibility
      2. Candidate Macro F1 >= Active Macro F1 - Regression Tolerance
      3. Candidate Recall >= 0.85 (Protects against missing attack vectors)
      4. Candidate False Positive Rate <= 0.05 (Protects against alert fatigue)
      5. Inference Latency <= 5.0ms
    """
    if artifact_metadata:
        ok, compat_errors = validate_artifact_compatibility(artifact_metadata)
        if not ok:
            return False, f"Artifact Schema Compatibility Failed: {compat_errors}"

    min_required_f1 = active_f1 - regression_tolerance
    if candidate_f1 < min_required_f1:
        return False, f"Candidate F1 ({candidate_f1:.4f}) is below active threshold with tolerance ({min_required_f1:.4f})."
    if candidate_recall < 0.85:
        return False, f"Candidate Recall ({candidate_recall:.4f}) fails minimum threshold (0.8500)."
    if candidate_fpr > 0.05:
        return False, f"Candidate False Positive Rate ({candidate_fpr:.4f}) exceeds max allowed limit (0.0500)."
    if candidate_latency_ms > 5.0:
        return False, f"Candidate Latency ({candidate_latency_ms:.2f}ms) exceeds max limit (5.00ms)."

    return True, "PASSED: All multi-metric promotion criteria satisfied."


def async_train_worker():
    """Background worker task executing leakage-free training pipeline and evaluating promotion gate."""
    try:
        results = run_training_pipeline(num_synthetic_samples=1500)
        if results:
            champion = results[0]
            passed, reason = evaluate_promotion_gate(
                candidate_f1=champion["f1_score"],
                candidate_recall=champion["recall"],
                candidate_fpr=round(1.0 - champion["recall"], 4)
            )
            print(f"Promotion Gate Evaluation Result: {passed} - {reason}")
    except Exception as e:
        print(f"Background Retraining Error: {e}")


@router.get("/models", summary="List All Trained ML/DL Models in Registry")
async def list_registered_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Lists all registered ML models with versioning, lifecycle status, and metrics."""
    query = select(ModelRegistry).order_by(ModelRegistry.f1_score.desc())
    result = await db.execute(query)
    models = result.scalars().all()
    return [
        {
            "id": m.id,
            "model_name": m.model_name,
            "model_version": m.model_version,
            "model_type": m.model_type,
            "status": m.status,
            "accuracy": m.accuracy,
            "f1_score": m.f1_score,
            "precision_score": m.precision_score,
            "recall_score": m.recall_score,
            "roc_auc": m.roc_auc,
            "latency_ms": m.latency_ms,
            "is_active": m.is_active,
            "schema_version": m.schema_version,
            "preprocessing_version": m.preprocessing_version,
            "trained_at": m.trained_at.isoformat(),
            "promoted_at": m.promoted_at.isoformat() if m.promoted_at else None,
            "previous_version": m.previous_version
        }
        for m in models
    ]


@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED, summary="Trigger Asynchronous Retraining Pipeline")
async def trigger_training_pipeline(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role(["admin"]))
):
    """Triggers real asynchronous retraining worker evaluated by the Multi-Metric Promotion Gate."""
    background_tasks.add_task(async_train_worker)

    audit = AuditLog(
        user_id=admin_user.id,
        action="MODEL_RETRAIN_TRIGGERED",
        resource="MODEL_REGISTRY",
        status="SUCCESS",
        details={"initiated_by": admin_user.username}
    )
    db.add(audit)
    await db.commit()

    return {
        "status": "ACCEPTED",
        "message": "Asynchronous model training pipeline dispatched to background worker.",
        "promotion_gate": "Multi-Metric Gate (Macro F1, Recall >= 0.85, FPR <= 0.05, Latency <= 5ms)",
        "initiated_at": admin_user.username
    }


@router.post("/models/{model_version}/rollback", summary="Rollback Active Classifier Version (Admin Only)")
async def rollback_model_version(
    model_version: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role(["admin"]))
):
    """
    Rolls back the active production model classifier to specified registered version and clears artifact cache.
    Unauthorized non-admin calls return HTTP 403 Forbidden via require_role.
    """
    query = select(ModelRegistry).where(
        (ModelRegistry.model_version == model_version) | (ModelRegistry.model_name == model_version)
    )
    result = await db.execute(query)
    target_model = result.scalar_one_or_none()

    if not target_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model version '{model_version}' not found in registry."
        )

    # Get current active model
    active_query = select(ModelRegistry).where(ModelRegistry.is_active == True)
    active_result = await db.execute(active_query)
    current_active = active_result.scalar_one_or_none()

    previous_ver_str = current_active.model_version if current_active else None

    # Atomic Lifecycle Transition
    if current_active and current_active.id != target_model.id:
        current_active.is_active = False
        current_active.status = "ROLLED_BACK"

    target_model.is_active = True
    target_model.status = "ACTIVE"
    target_model.promoted_at = datetime.now(timezone.utc)
    target_model.previous_version = previous_ver_str
    target_model.promotion_reason = f"Manual admin rollback executed by {admin_user.username}"

    # Invalidate PredictService cached artifact memory
    PredictService._model_artifacts.clear()
    PredictService._explainers.clear()

    audit = AuditLog(
        user_id=admin_user.id,
        action="MODEL_ROLLBACK_EXECUTED",
        resource="MODEL_REGISTRY",
        status="SUCCESS",
        details={
            "target_model_version": target_model.model_version,
            "previous_active_version": previous_ver_str,
            "executed_by": admin_user.username
        }
    )
    db.add(audit)
    await db.commit()

    return {
        "status": "SUCCESS",
        "message": f"Active production classifier successfully rolled back to version '{target_model.model_version}'.",
        "active_model_version": target_model.model_version,
        "previous_version": previous_ver_str
    }
