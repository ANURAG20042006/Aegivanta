from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
import json
import hashlib
import joblib
from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db, AsyncSessionFactory
from backend.app.models.user import User
from backend.app.models.model_registry import ModelRegistry
from backend.app.models.training_job import TrainingJob
from backend.app.models.audit_log import AuditLog
from backend.app.core.dependencies import require_role
from backend.app.services.predict_service import PredictService
from ml.train_pipeline import run_training_pipeline
from ml.schema.feature_schema import validate_artifact_compatibility

router = APIRouter(prefix="/train", tags=["Model Training & Registry Lifecycle"])

MAX_INFERENCE_LATENCY_MS: float = 5.0
MIN_REQUIRED_RECALL: float = 0.85
MAX_ALLOWED_FPR: float = 0.05
DEFAULT_REGRESSION_TOLERANCE: float = 0.01


def evaluate_promotion_gate(
    candidate_f1: Optional[float],
    candidate_recall: Optional[float],
    candidate_fpr: Optional[float],
    candidate_latency_ms: Optional[float] = None,
    active_f1: Optional[float] = None,
    regression_tolerance: float = DEFAULT_REGRESSION_TOLERANCE,
    artifact_metadata: Optional[Dict[str, Any]] = None,
    candidate_per_class_metrics: Optional[Dict[str, Dict[str, float]]] = None,
    active_per_class_metrics: Optional[Dict[str, Dict[str, float]]] = None,
    protected_metrics: Optional[List[str]] = None
) -> Tuple[bool, str]:
    """
    Multi-Metric Promotion Gate with Per-Class Regression Protection.

    FIRST-MODEL PROMOTION POLICY (active_f1 is None):
      When no active model exists, the candidate is evaluated against absolute
      safety thresholds only.  No active F1 is fabricated or assumed.
      Checks: F1 available, Recall >= MIN_REQUIRED_RECALL, FPR <= MAX_ALLOWED_FPR,
              Latency <= MAX_INFERENCE_LATENCY_MS.

    SUBSEQUENT PROMOTION POLICY (active_f1 is a real measured value):
      1. Artifact Integrity & Schema Compatibility
      2. Required Metric Presence (F1, Recall, FPR, Latency must be non-None)
      3. Candidate Macro F1 >= Active Macro F1 - Regression Tolerance
      4. Candidate Recall >= MIN_REQUIRED_RECALL (0.85)
      5. Candidate FPR <= MAX_ALLOWED_FPR (0.05)
      6. Inference Latency <= MAX_INFERENCE_LATENCY_MS (5.0ms)
      7. Per-Class Regression Protection & Class Set Matching
    """
    if artifact_metadata:
        ok, compat_errors = validate_artifact_compatibility(artifact_metadata)
        if not ok:
            return False, f"Artifact Schema Compatibility Failed: {compat_errors}"

    # Required metric availability — applies in both first-model and subsequent promotion
    if candidate_f1 is None:
        return False, "Promotion rejected: Macro F1 metric unavailable. Cannot promote without a real measured F1 score."
    if candidate_recall is None:
        return False, "Promotion rejected: Recall metric unavailable. Cannot promote without a real measured Recall score."
    if candidate_fpr is None:
        return False, "Promotion rejected: FPR metric unavailable. Cannot promote without a real measured False Positive Rate."
    if candidate_latency_ms is None:
        return False, "Promotion rejected: inference latency unavailable."

    # Absolute safety thresholds — always enforced
    if candidate_recall < MIN_REQUIRED_RECALL:
        return False, f"Candidate Recall ({candidate_recall:.4f}) fails minimum threshold ({MIN_REQUIRED_RECALL:.4f})."
    if candidate_fpr > MAX_ALLOWED_FPR:
        return False, f"Candidate False Positive Rate ({candidate_fpr:.4f}) exceeds max allowed limit ({MAX_ALLOWED_FPR:.4f})."
    if candidate_latency_ms > MAX_INFERENCE_LATENCY_MS:
        return False, f"Promotion rejected: Candidate Latency ({candidate_latency_ms:.2f}ms) exceeds max limit ({MAX_INFERENCE_LATENCY_MS:.2f}ms)."

    if active_f1 is None:
        # First-model promotion: no active baseline — absolute thresholds already checked above.
        # Relative regression check is skipped because there is no baseline to regress from.
        return True, "PASSED: First-model promotion — absolute safety thresholds satisfied (no active baseline to compare against)."

    # Relative F1 regression check — only when a real active_f1 measurement is available
    min_required_f1 = active_f1 - regression_tolerance
    if candidate_f1 < min_required_f1 - 1e-6:
        return False, f"Candidate F1 ({candidate_f1:.4f}) is below active threshold with tolerance ({min_required_f1:.4f})."

    # Per-Class Metrics & Regression Protection Check
    if active_per_class_metrics is not None:
        if candidate_per_class_metrics is None:
            return False, "Promotion rejected: per-class metrics unavailable."

        cand_classes = set(candidate_per_class_metrics.keys())
        active_classes = set(active_per_class_metrics.keys())
        if cand_classes != active_classes:
            return False, f"Promotion rejected: Candidate class set {sorted(list(cand_classes))} does not match active model class set {sorted(list(active_classes))}."

        metrics_to_check = protected_metrics or ["recall"]
        for cls_name, act_metrics in active_per_class_metrics.items():
            cand_metrics = candidate_per_class_metrics.get(cls_name)
            if cand_metrics is None:
                return False, f"Promotion rejected: per-class metrics missing for class {cls_name}."

            for m_name in metrics_to_check:
                if m_name in act_metrics:
                    if m_name not in cand_metrics or cand_metrics[m_name] is None:
                        return False, f"Promotion rejected: {cls_name} {m_name} metric unavailable."
                    act_val = float(act_metrics[m_name])
                    cand_val = float(cand_metrics[m_name])
                    allowed_min = act_val - regression_tolerance
                    if cand_val < allowed_min - 1e-6:
                        act_str = f"{act_val:.2f}" if abs(act_val - round(act_val, 2)) < 1e-5 else f"{act_val:.4f}"
                        cand_str = f"{cand_val:.2f}" if abs(cand_val - round(cand_val, 2)) < 1e-5 else f"{cand_val:.4f}"
                        tol_str = f"{regression_tolerance:.2f}" if abs(regression_tolerance - round(regression_tolerance, 2)) < 1e-5 else f"{regression_tolerance:.4f}"
                        return False, f"Promotion rejected: {cls_name} {m_name} regressed from {act_str} to {cand_str}, exceeding tolerance {tol_str}."

    return True, "PASSED: All multi-metric promotion criteria satisfied."


def verify_rollback_artifact_integrity(
    target_model: ModelRegistry,
    artifacts_dir: Optional[Path] = None
) -> Tuple[bool, str]:
    """
    12-Point Rollback Artifact Integrity Validation:
      1. Registry record exists.
      2. Artifact path exists.
      3. Model artifact loads successfully.
      4. Preprocessor artifact exists.
      5. Preprocessor loads successfully.
      6. Feature schema exists.
      7. Schema version is compatible.
      8. Model feature dimensions match preprocessor.
      9. Metadata exists.
      10. Hash/checksum matches when stored.
      11. Version compatibility check.
      12. Model object usability check for inference.
    """
    if not target_model:
        return False, "Rollback rejected: Target model registry record does not exist."

    repo_root = Path(__file__).resolve().parents[3]
    if artifacts_dir is None:
        artifacts_dir = repo_root / "ml/artifacts"
    elif not artifacts_dir.is_absolute():
        artifacts_dir = repo_root / artifacts_dir

    art_path = Path(target_model.artifact_path)
    if not art_path.is_absolute():
        candidates = [
            Path.cwd() / art_path,
            repo_root / art_path,
            artifacts_dir / art_path.name
        ]
        resolved_path = None
        for c in candidates:
            if c.exists():
                resolved_path = c
                break
        if resolved_path is None:
            return False, f"Rollback rejected: Target model artifact file '{target_model.artifact_path}' does not exist on disk."
        art_path = resolved_path
    elif not art_path.exists():
        return False, f"Rollback rejected: Target model artifact file '{target_model.artifact_path}' does not exist on disk."

    try:
        model = joblib.load(art_path)
    except Exception as exc:
        return False, f"Rollback rejected: Target model artifact file '{art_path}' is corrupted or unloadable: {exc}"

    prep_path = artifacts_dir / "preprocessor.joblib"
    if not prep_path.exists():
        prep_path = Path.cwd() / "ml/artifacts/preprocessor.joblib"
    if not prep_path.exists():
        return False, f"Rollback rejected: Preprocessor artifact file '{prep_path}' does not exist."

    try:
        preprocessor = joblib.load(prep_path)
    except Exception as exc:
        return False, f"Rollback rejected: Preprocessor artifact file '{prep_path}' is corrupted or unloadable: {exc}"

    meta_path = artifacts_dir / "metadata.json"
    if not meta_path.exists():
        meta_path = Path.cwd() / "ml/artifacts/metadata.json"
    if not meta_path.exists():
        return False, f"Rollback rejected: Artifact metadata file '{meta_path}' does not exist."

    try:
        with meta_path.open("r", encoding="utf-8") as f:
            metadata = json.load(f)
    except Exception as exc:
        return False, f"Rollback rejected: Artifact metadata file '{meta_path}' is corrupted JSON: {exc}"

    compat_ok, compat_errors = validate_artifact_compatibility(metadata)
    if not compat_ok:
        return False, f"Rollback rejected: Artifact schema compatibility failed: {compat_errors}"

    inner_model = getattr(model, "model", model)
    n_features_in = getattr(inner_model, "n_features_in_", None)
    if (not n_features_in or n_features_in == 0) and hasattr(inner_model, "feature_names_") and inner_model.feature_names_:
        n_features_in = len(inner_model.feature_names_)
    elif (not n_features_in or n_features_in == 0) and hasattr(inner_model, "_input_dim") and inner_model._input_dim:
        n_features_in = inner_model._input_dim

    selected_feats = len(getattr(preprocessor, "selected_feature_names", []))
    if n_features_in and n_features_in > 0 and selected_feats > 0 and n_features_in != selected_feats:
        return False, f"Rollback rejected: Preprocessor produces {selected_feats} features but target model expects {n_features_in} features."

    # 10. Checksum / SHA-256 Hash Verification (Fail-Closed)
    expected_hash = getattr(target_model, "artifact_sha256", None)

    manifest_path = artifacts_dir / "artifact_manifest.json"
    if not manifest_path.exists():
        manifest_path = Path.cwd() / "ml/artifacts/artifact_manifest.json"

    if expected_hash is None and manifest_path.exists():
        try:
            with manifest_path.open("r", encoding="utf-8") as f:
                manifest = json.load(f)
            expected_hash = manifest.get("model_hash")
        except Exception as exc:
            return False, f"Rollback rejected: Artifact manifest file is corrupted or unreadable: {exc}"

    if expected_hash:
        try:
            actual_hash = hashlib.sha256(art_path.read_bytes()).hexdigest()
        except Exception as exc:
            return False, f"Rollback rejected: Failed to calculate artifact SHA-256 hash: {exc}"

        if actual_hash != expected_hash:
            return False, f"Rollback rejected: Model artifact SHA-256 hash mismatch ({actual_hash[:8]} vs registered {expected_hash[:8]})."

    # 11 & 12. Inference usability check
    if not hasattr(model, "predict"):
        return False, "Rollback rejected: Target model object missing required predict() interface."

    return True, "PASSED: Rollback artifact integrity verified."


async def async_train_worker(job_id: str):
    """
    Persisted Background Worker Task:
    Transitions job & model lifecycle states:
    TRAINING -> CANDIDATE -> (PROMOTION GATE) -> ACTIVE / REJECTED
    """
    async with AsyncSessionFactory() as db:
        query = select(TrainingJob).where(TrainingJob.id == job_id)
        res = await db.execute(query)
        job = res.scalar_one_or_none()

        if not job:
            return

        job.status = "RUNNING"
        await db.commit()

        try:
            results = run_training_pipeline(num_synthetic_samples=1500)
            if not results:
                job.status = "FAILED"
                job.error_message = "Training pipeline returned empty leaderboard results."
                job.finished_at = datetime.now(timezone.utc)
                await db.commit()
                return

            champion = results[0]
            candidate_version = f"{champion['model_name'].lower().replace(' ', '_')}-v1.0"
            job.candidate_version = candidate_version
            job.metrics = {
                "accuracy": champion.get("cv_accuracy_mean"),
                "f1_score": champion.get("cv_f1_mean"),
                "precision": champion.get("cv_precision_mean"),
                "recall": champion.get("cv_recall_mean"),
                "fpr": champion.get("cv_fpr_mean")
            }

            # Evaluate against active production model
            active_query = select(ModelRegistry).where(ModelRegistry.is_active == True)
            active_res = await db.execute(active_query)
            active_model = active_res.scalar_one_or_none()
            # active_f1 is the real measured F1 of the current production model.
            # When no active model exists, active_f1=None — evaluate_promotion_gate
            # applies first-model absolute thresholds only. Never fabricate a metric.
            active_f1: Optional[float] = active_model.f1_score if active_model else None

            meta_path = Path("ml/artifacts/metadata.json")
            candidate_roc_auc = None
            if meta_path.exists():
                try:
                    with meta_path.open("r", encoding="utf-8") as f:
                        meta_data = json.load(f)
                    candidate_roc_auc = meta_data.get("final_test_metrics", {}).get("roc_auc")
                except Exception:
                    pass

            candidate_fpr = champion.get("cv_fpr_mean")
            candidate_latency = champion.get("cv_latency_ms")
            candidate_per_class = champion.get("per_class_metrics")
            active_per_class = getattr(active_model, "per_class_metrics", None) if active_model else None

            from ml.schema.artifact_mapping import resolve_model_artifact_path
            cand_art_file, cand_art_type, cand_sha256, cand_exists = resolve_model_artifact_path(champion["model_name"])

            # Register Candidate Model in ModelRegistry with status "CANDIDATE" BEFORE promotion gate evaluation
            candidate_registry = ModelRegistry(
                model_name=champion["model_name"],
                model_version=candidate_version,
                model_type=champion["model_type"],
                status="CANDIDATE",
                accuracy=champion.get("cv_accuracy_mean"),
                f1_score=champion.get("cv_f1_mean"),
                precision_score=champion.get("cv_precision_mean"),
                recall_score=champion.get("cv_recall_mean"),
                roc_auc=candidate_roc_auc,
                latency_ms=champion.get("cv_latency_ms"),
                artifact_sha256=cand_sha256,
                is_active=False,
                artifact_path=str(cand_art_file).replace("\\", "/"),
                artifact_type=cand_art_type,
                previous_version=active_model.model_version if active_model else None,
                per_class_metrics=candidate_per_class
            )
            db.add(candidate_registry)
            await db.commit()
            await db.refresh(candidate_registry)

            # Evaluate Promotion Gate
            passed, reason = evaluate_promotion_gate(
                candidate_f1=champion.get("cv_f1_mean"),
                candidate_recall=champion.get("cv_recall_mean"),
                candidate_fpr=candidate_fpr,
                candidate_latency_ms=candidate_latency,
                active_f1=active_f1,
                candidate_per_class_metrics=candidate_per_class,
                active_per_class_metrics=active_per_class
            )
            candidate_registry.promotion_reason = reason
            job.promotion_reason = reason

            if passed:
                if active_model:
                    active_model.is_active = False
                    active_model.status = "ARCHIVED"

                candidate_registry.status = "ACTIVE"
                candidate_registry.is_active = True
                candidate_registry.promoted_at = datetime.now(timezone.utc)
                job.status = "PROMOTED"

                PredictService._model_artifacts.clear()
                PredictService._preprocessor_artifact = None
                PredictService._explainers.clear()
            else:
                candidate_registry.status = "REJECTED"
                candidate_registry.is_active = False
                job.status = "REJECTED"

            job.finished_at = datetime.now(timezone.utc)
            await db.commit()

        except Exception as exc:
            job.status = "FAILED"
            job.error_message = str(exc)
            job.finished_at = datetime.now(timezone.utc)
            await db.commit()


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
            "previous_version": m.previous_version,
            "per_class_metrics": m.per_class_metrics
        }
        for m in models
    ]


@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED, summary="Trigger Asynchronous Retraining Pipeline")
async def trigger_training_pipeline(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role(["admin"]))
):
    """
    Creates a persisted TrainingJob (QUEUED state) before returning job_id, status, and created_at.
    Dispatches background worker to execute retraining pipeline.
    """
    job = TrainingJob(
        user_id=admin_user.id,
        status="QUEUED",
        model_name="XGBoost Classifier"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    background_tasks.add_task(async_train_worker, job.id)

    audit = AuditLog(
        user_id=admin_user.id,
        action="MODEL_RETRAIN_TRIGGERED",
        resource="MODEL_REGISTRY",
        status="SUCCESS",
        details={"job_id": job.id, "initiated_by": admin_user.username}
    )
    db.add(audit)
    await db.commit()

    return {
        "job_id": job.id,
        "status": job.status,
        "created_at": job.created_at.isoformat(),
        "message": "Model retraining job created and queued for background worker execution."
    }


@router.get("/jobs", summary="List All Retraining Jobs")
async def list_training_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Lists all historical retraining background jobs."""
    query = select(TrainingJob).order_by(TrainingJob.created_at.desc())
    res = await db.execute(query)
    jobs = res.scalars().all()
    return [
        {
            "job_id": j.id,
            "status": j.status,
            "model_name": j.model_name,
            "candidate_version": j.candidate_version,
            "metrics": j.metrics,
            "error_message": j.error_message,
            "promotion_reason": j.promotion_reason,
            "created_at": j.created_at.isoformat(),
            "finished_at": j.finished_at.isoformat() if j.finished_at else None
        }
        for j in jobs
    ]


@router.get("/jobs/{job_id}", summary="Get Status of Specific Retraining Job")
async def get_training_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Gets status and metric details of a specific retraining background job."""
    query = select(TrainingJob).where(TrainingJob.id == job_id)
    res = await db.execute(query)
    job = res.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Retraining job '{job_id}' not found."
        )

    return {
        "job_id": job.id,
        "status": job.status,
        "model_name": job.model_name,
        "candidate_version": job.candidate_version,
        "metrics": job.metrics,
        "error_message": job.error_message,
        "promotion_reason": job.promotion_reason,
        "created_at": job.created_at.isoformat(),
        "finished_at": job.finished_at.isoformat() if job.finished_at else None
    }


@router.post("/models/{model_version}/rollback", summary="Rollback Active Classifier Version (Admin Only)")
async def rollback_model_version(
    model_version: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role(["admin"]))
):
    """
    Rolls back active production classifier to specified registered version after verifying 12-point artifact integrity.
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

    # 12-Point Artifact Integrity Check BEFORE any active model changes!
    ok, err_msg = verify_rollback_artifact_integrity(target_model)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=err_msg
        )

    # Get current active model
    active_query = select(ModelRegistry).where(ModelRegistry.is_active == True)
    active_result = await db.execute(active_query)
    current_active = active_result.scalar_one_or_none()

    previous_ver_str = current_active.model_version if current_active else None

    # Atomic Lifecycle Transition
    if current_active and current_active.id != target_model.id:
        current_active.is_active = False
        current_active.status = "ARCHIVED"

    target_model.is_active = True
    target_model.status = "ACTIVE"
    target_model.promoted_at = datetime.now(timezone.utc)
    target_model.previous_version = previous_ver_str
    target_model.promotion_reason = f"Manual admin rollback executed by {admin_user.username}"

    # Invalidate PredictService cached artifact memory
    PredictService._model_artifacts.clear()
    PredictService._preprocessor_artifact = None
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
