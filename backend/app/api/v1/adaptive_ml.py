"""
backend/app/api/v1/adaptive_ml.py
=================================
Phase 3.10 Adaptive ML Detection Intelligence & Model Governance API Router.
Exposes 5-domain adaptive inference, concept drift monitoring, model governance/approval lifecycle,
and analyst feedback loop endpoints with strict RBAC enforcement.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.audit_log import AuditLog
from backend.app.core.dependencies import require_role
from backend.app.services.adaptive_detection_service import adaptive_detection_service
from backend.app.services.model_governance_service import ModelGovernanceService
from backend.app.services.feedback_service import FeedbackService
from backend.app.services.soc_event_broadcaster import soc_broadcaster

router = APIRouter(prefix="/ml", tags=["Adaptive ML Detection & Model Governance"])


# Pydantic Schemas
class AdaptiveDetectionRequest(BaseModel):
    features: Dict[str, Any] = Field(..., description="Network flow features dictionary (78 CIC-IDS2017 keys)")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional telemetry context (source_ip, user_id, etc.)")


class BatchAdaptiveDetectionRequest(BaseModel):
    items: List[AdaptiveDetectionRequest] = Field(..., description="List of feature dictionaries to classify")


class FeedbackSubmissionRequest(BaseModel):
    predicted_attack_type: str
    actual_verdict: str = Field(..., description="TRUE_POSITIVE, FALSE_POSITIVE, BENIGN, UNKNOWN")
    predicted_confidence: Optional[float] = None
    incident_id: Optional[str] = None
    detection_id: Optional[str] = None
    flow_id: Optional[str] = None
    corrected_attack_type: Optional[str] = None
    notes: Optional[str] = None
    feature_snapshot: Optional[Dict[str, Any]] = None


class ModelApprovalRequest(BaseModel):
    notes: Optional[str] = Field(default=None, description="Analyst review notes and validation sign-off")


class ModelRejectionRequest(BaseModel):
    reason: str = Field(..., description="Documented rationale for model rejection")


class ModelRollbackRequest(BaseModel):
    rollback_reason: str = Field(..., description="Documented justification for active model rollback")


# 1. ADAPTIVE INFERENCE ENDPOINTS
@router.post("/adaptive-detect", summary="Execute 5-Domain Adaptive Threat Detection")
async def execute_adaptive_detection(
    payload: AdaptiveDetectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """
    Evaluates telemetry flow across 5 domains:
    1. Multi-Model ML Ensemble (CatBoost, LightGBM, Random Forest, Decision Tree)
    2. Authoritative Deterministic Detection Rules
    3. Statistical Behavioral Baselines (Z-score deviations)
    4. Threat Intelligence Fast IOC Cache
    5. Attack Graph & Lateral Movement Proximity
    """
    result = await adaptive_detection_service.detect_adaptive_flow(
        features_dict=payload.features,
        context_event=payload.context,
        db=db
    )
    return result


@router.post("/adaptive-detect-batch", summary="Execute Batch Adaptive Detection")
async def execute_batch_adaptive_detection(
    payload: BatchAdaptiveDetectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Executes adaptive detection across a batch of flow vectors."""
    results = []
    for item in payload.items:
        res = await adaptive_detection_service.detect_adaptive_flow(
            features_dict=item.features,
            context_event=item.context,
            db=db
        )
        results.append(res)

    malicious_count = sum(1 for r in results if r["is_malicious"])
    return {
        "total_processed": len(results),
        "malicious_count": malicious_count,
        "results": results
    }


# 2. CONCEPT DRIFT MONITORING ENDPOINTS
@router.get("/drift-status", summary="Get Current Production Drift Status")
async def get_drift_status(
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Retrieves current production drift accumulation status and PSI thresholds."""
    summary = adaptive_detection_service.drift_detector.get_current_drift_summary()
    return summary


@router.post("/evaluate-drift", summary="Trigger Production Drift Window Evaluation")
async def trigger_drift_evaluation(
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Executes KS-tests and PSI drift analysis on accumulated production observations."""
    results = adaptive_detection_service.drift_detector.evaluate_drift()

    if results.get("alert_status") in ["WARNING", "CRITICAL"]:
        await soc_broadcaster.broadcast(
            category="SYSTEM_ALERT",
            severity="WARNING" if results.get("alert_status") == "WARNING" else "CRITICAL",
            title="Concept Drift Detected",
            description=f"Drift monitoring status is {results.get('status')}. Max feature PSI: {results.get('statistics', {}).get('max_feature_psi', 0.0)}.",
            details=results
        )

    return results


# 3. ANALYST FEEDBACK LOOP ENDPOINTS
@router.post("/feedback", summary="Submit Analyst Triage Feedback")
async def submit_analyst_feedback(
    payload: FeedbackSubmissionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Captures analyst ground-truth feedback (TRUE_POSITIVE, FALSE_POSITIVE, BENIGN, UNKNOWN)."""
    res = await FeedbackService.record_feedback(
        db=db,
        predicted_attack_type=payload.predicted_attack_type,
        actual_verdict=payload.actual_verdict,
        predicted_confidence=payload.predicted_confidence,
        incident_id=payload.incident_id,
        detection_id=payload.detection_id,
        flow_id=payload.flow_id,
        corrected_attack_type=payload.corrected_attack_type,
        analyst_user_id=current_user.id,
        analyst_username=current_user.username,
        notes=payload.notes,
        feature_snapshot=payload.feature_snapshot
    )
    return res


@router.get("/feedback/stats", summary="Get Feedback & Analyst Accuracy Metrics")
async def get_feedback_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Retrieves empirical accuracy, precision, and false-positive rates from analyst feedback."""
    stats_data = await FeedbackService.get_feedback_stats(db)
    return stats_data


@router.get("/feedback", summary="List Analyst Feedback Records")
async def list_feedback_records(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    verdict: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Lists recorded analyst feedback triage items."""
    records = await FeedbackService.list_feedback(db=db, limit=limit, offset=offset, verdict=verdict)
    return records


@router.get("/feedback/export", summary="Export Supervised Retraining Dataset")
async def export_retraining_dataset(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Compiles validated feedback records into training dataset format."""
    dataset = await FeedbackService.export_retraining_dataset(db)
    return dataset


# 4. MODEL GOVERNANCE & LIFECYCLE ENDPOINTS
@router.get("/registry", summary="List Registered Models with Governance Metadata")
async def list_model_registry(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Lists registered models with accuracy, F1, latency, approval status, and deployment status."""
    models = await ModelGovernanceService.list_models(db=db, status_filter=status)
    return models


@router.get("/registry/{model_id}", summary="Get Model Details & Confusion Matrix")
async def get_model_registry_details(
    model_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """Retrieves comprehensive metadata and per-class performance metrics for a model."""
    model = await ModelGovernanceService.get_model(db=db, model_id=model_id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found in registry")
    return model


@router.post("/registry/{model_id}/approve", summary="Approve Model for Promotion")
async def approve_model_version(
    model_id: str,
    payload: ModelApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Approves a candidate model after analyst review and validation."""
    res = await ModelGovernanceService.approve_model(
        db=db,
        model_id=model_id,
        analyst_username=current_user.username,
        notes=payload.notes
    )
    return res


@router.post("/registry/{model_id}/reject", summary="Reject Model Version")
async def reject_model_version(
    model_id: str,
    payload: ModelRejectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """Rejects a model candidate with documented rationale."""
    res = await ModelGovernanceService.reject_model(
        db=db,
        model_id=model_id,
        analyst_username=current_user.username,
        reason=payload.reason
    )
    return res


@router.post("/registry/{model_id}/activate", summary="Activate Approved Model to Production")
async def activate_model_to_production(
    model_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Promotes an APPROVED model to ACTIVE production status after passing safety promotion gate.
    Strictly requires ADMIN role.
    """
    res = await ModelGovernanceService.activate_approved_model(
        db=db,
        model_id=model_id,
        actor_username=current_user.username
    )
    return res


@router.post("/registry/{model_id}/rollback", summary="Rollback Active Production Model")
async def rollback_production_model(
    model_id: str,
    payload: ModelRollbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Rolls back the active model to a specified previous version.
    Strictly requires ADMIN role.
    """
    res = await ModelGovernanceService.rollback_to_version(
        db=db,
        target_model_id=model_id,
        actor_username=current_user.username,
        rollback_reason=payload.rollback_reason
    )
    return res
