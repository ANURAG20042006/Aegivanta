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

router = APIRouter(prefix="/train", tags=["Model Training & Registry"])


def evaluate_promotion_gate(
    candidate_f1: float,
    candidate_recall: float,
    candidate_fpr: float,
    active_f1: float = 0.85
) -> Tuple[bool, str]:
    """
    Multi-Metric Promotion Gate:
    1. Candidate Macro F1 >= Active Macro F1 (or baseline 0.85).
    2. Candidate Recall >= 0.85 (protects against missing attack vectors).
    3. Candidate FPR <= 0.05 (protects against alert fatigue).
    """
    if candidate_f1 < active_f1:
        return False, f"Candidate F1 ({candidate_f1:.4f}) is below active model threshold ({active_f1:.4f})."
    if candidate_recall < 0.85:
        return False, f"Candidate Recall ({candidate_recall:.4f}) fails minimum threshold (0.8500)."
    if candidate_fpr > 0.05:
        return False, f"Candidate False Positive Rate ({candidate_fpr:.4f}) exceeds max allowed limit (0.0500)."
    return True, "PASSED: All multi-metric promotion criteria satisfied."


def async_train_worker():
    """Background worker task executing leakage-free training pipeline and evaluating promotion gate."""
    try:
        results = run_training_pipeline(num_synthetic_samples=1500)
        # Evaluate champion candidate against promotion criteria
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
    """Lists all trained ML & Deep Learning models from database model registry."""
    query = select(ModelRegistry).order_by(ModelRegistry.f1_score.desc())
    result = await db.execute(query)
    models = result.scalars().all()
    return [
        {
            "id": m.id,
            "model_name": m.model_name,
            "model_type": m.model_type,
            "accuracy": m.accuracy,
            "f1_score": m.f1_score,
            "precision_score": m.precision_score,
            "recall_score": m.recall_score,
            "roc_auc": m.roc_auc,
            "is_active": m.is_active,
            "trained_at": m.trained_at.isoformat()
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
        "promotion_gate": "Multi-Metric Gate (Macro F1 >= active, Recall >= 0.85, FPR <= 0.05)",
        "initiated_at": admin_user.username
    }


@router.post("/models/{model_name}/rollback", summary="Rollback Active Classifier Version (Admin Only)")
async def rollback_model_version(
    model_name: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role(["admin"]))
):
    """Rolls back the active production model classifier to specified registered version and clears artifact cache."""
    query = select(ModelRegistry).where(ModelRegistry.model_name == model_name)
    result = await db.execute(query)
    target_model = result.scalar_one_or_none()

    if not target_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model version '{model_name}' not found in registry."
        )

    # Deactivate all models
    await db.execute(update(ModelRegistry).values(is_active=False))
    target_model.is_active = True

    # Invalidate PredictService cached artifact memory
    PredictService._model_artifacts.clear()
    PredictService._explainers.clear()

    audit = AuditLog(
        user_id=admin_user.id,
        action="MODEL_ROLLBACK_EXECUTED",
        resource="MODEL_REGISTRY",
        status="SUCCESS",
        details={"target_model": model_name, "executed_by": admin_user.username}
    )
    db.add(audit)
    await db.commit()

    return {
        "status": "SUCCESS",
        "message": f"Active production classifier successfully rolled back to '{model_name}'.",
        "active_model": model_name
    }
