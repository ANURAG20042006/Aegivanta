from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.multi_model_detection_service import MultiModelDetectionService
from backend.app.services.model_security_governance_service import ModelSecurityGovernanceService
from backend.app.services.model_drift_monitoring_service import ModelDriftMonitoringService
from backend.app.services.adversarial_defense_service import AdversarialDefenseService
from backend.app.services.ai_copilot_v2_service import AICopilotV2Service
from backend.app.models.ai_security_intelligence import AIAdversarialEvent, AIModelGovernance
from backend.app.core.exceptions import SentinelAIException

router = APIRouter(prefix="/ai-intel", tags=["Advanced AI/ML Security Intelligence"])


class RegisterModelRequest(BaseModel):
    model_name: str
    model_version: str
    model_family: Optional[str] = "SUPERVISED_ENSEMBLE"
    framework: Optional[str] = "SCIKIT_LEARN"
    artifact_path: str
    artifact_sha256: str
    training_dataset_name: Optional[str] = "CIC-IDS2017-Production-Split"
    training_samples_count: Optional[int] = 50000
    features_list: Optional[List[str]] = []
    roc_auc: Optional[float] = 0.985
    precision_score: Optional[float] = 0.962
    recall_score: Optional[float] = 0.954
    f1_score: Optional[float] = 0.958


class PromoteModelRequest(BaseModel):
    target_stage: str = "PRODUCTION"


class MultiModelInferenceRequest(BaseModel):
    features: Dict[str, float]
    entity_id: Optional[str] = None


class CopilotReasonRequest(BaseModel):
    prompt: str
    incident_id: Optional[str] = None


@router.get("/models", summary="List Registered Models")
async def list_models(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all registered ML models with governance, lineage, and cryptographic signatures."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ModelSecurityGovernanceService.list_models(db, tenant_id)


@router.post("/models/register", summary="Register Model Version")
async def register_model(
    payload: RegisterModelRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Registers a new model version with HMAC-SHA256 signature generation."""
    tenant_id = context.tenant_id or "default-tenant"
    sig = ModelSecurityGovernanceService.generate_artifact_signature(payload.artifact_sha256)

    model = AIModelGovernance(
        tenant_id=tenant_id,
        model_name=payload.model_name,
        model_version=payload.model_version,
        model_family=payload.model_family or "SUPERVISED_ENSEMBLE",
        framework=payload.framework or "SCIKIT_LEARN",
        stage="STAGING",
        is_active=False,
        artifact_path=payload.artifact_path,
        artifact_sha256=payload.artifact_sha256,
        artifact_signature=sig,
        signature_verified=True,
        training_dataset_name=payload.training_dataset_name or "CIC-IDS2017-Production-Split",
        training_samples_count=payload.training_samples_count or 50000,
        features_list=payload.features_list or [],
        roc_auc=payload.roc_auc or 0.985,
        precision_score=payload.precision_score or 0.962,
        recall_score=payload.recall_score or 0.954,
        f1_score=payload.f1_score or 0.958,
        created_by=context.user_id or "ML_ENGINEER"
    )
    db.add(model)
    await db.flush()

    return {"status": "REGISTERED", "model_id": model.id, "artifact_signature": sig}


@router.post("/models/{id}/promote", summary="Promote Model Lifecycle Stage")
async def promote_model(
    id: str,
    payload: PromoteModelRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Promotes a model stage (STAGING -> CANARY -> PRODUCTION)."""
    tenant_id = context.tenant_id or "default-tenant"
    promoted = await ModelSecurityGovernanceService.promote_model(
        db=db,
        tenant_id=tenant_id,
        model_id=id,
        target_stage=payload.target_stage,
        promoted_by=context.user_id or "ADMIN"
    )
    return {"status": "PROMOTED", "model_version": promoted.model_version, "stage": promoted.stage}


@router.post("/models/{id}/rollback", summary="Rollback Model Version")
async def rollback_model(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Rolls back a model version."""
    tenant_id = context.tenant_id or "default-tenant"
    rb = await ModelSecurityGovernanceService.rollback_model(db, tenant_id, id)
    return {"status": "ROLLED_BACK", "model_version": rb.model_version}


@router.post("/models/{id}/verify-signature", summary="Verify Model Cryptographic Integrity")
async def verify_signature(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Verifies HMAC-SHA256 signature for model artifact."""
    tenant_id = context.tenant_id or "default-tenant"
    stmt = select(AIModelGovernance).where(AIModelGovernance.id == id, AIModelGovernance.tenant_id == tenant_id)
    model = (await db.execute(stmt)).scalar_one_or_none()
    if not model:
        raise SentinelAIException(status_code=404, detail="Model not found.")

    is_valid = ModelSecurityGovernanceService.verify_artifact_signature(
        model.artifact_sha256,
        model.artifact_signature or ""
    )
    model.signature_verified = is_valid
    await db.flush()

    return {"is_valid": is_valid, "model_version": model.model_version, "artifact_sha256": model.artifact_sha256}


@router.get("/drift", summary="Get Model Drift & PSI State")
async def get_drift(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves feature and prediction drift metrics (PSI and KS-test)."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ModelDriftMonitoringService.get_latest_drift_metrics(db, tenant_id)


@router.get("/quality", summary="Get Detection Quality Benchmarks")
async def get_quality(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves precision, recall, F1, latency, and throughput metrics."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ModelDriftMonitoringService.get_detection_quality(db, tenant_id)


@router.post("/detect/multi-model", summary="Execute Multi-Model Detection Pipeline")
async def execute_multi_model(
    payload: MultiModelInferenceRequest,
    context: TenantContext = Depends(resolve_tenant_context)
):
    """Runs supervised, anomaly, behavioral, and ensemble scoring with XAI attribution."""
    tenant_id = context.tenant_id or "default-tenant"
    return MultiModelDetectionService.execute_multi_model_inference(
        features=payload.features,
        tenant_id=tenant_id,
        entity_id=payload.entity_id
    )


@router.get("/adversarial/events", summary="List Blocked Adversarial Attacks")
async def list_adversarial_events(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists mitigated adversarial attacks, prompt injections, and data poisoning attempts."""
    tenant_id = context.tenant_id or "default-tenant"
    stmt = (
        select(AIAdversarialEvent)
        .where(AIAdversarialEvent.tenant_id == tenant_id)
        .order_by(desc(AIAdversarialEvent.detected_at))
        .limit(30)
    )
    events = list((await db.execute(stmt)).scalars().all())
    return [
        {
            "id": e.id,
            "threat_type": e.threat_type,
            "source_ip": e.source_ip,
            "raw_payload_snippet": e.raw_payload_snippet,
            "mitigation_action": e.mitigation_action,
            "is_blocked": e.is_blocked,
            "details": e.details,
            "detected_at": e.detected_at.isoformat() if e.detected_at else None
        }
        for e in events
    ]


@router.post("/copilot/reason", summary="AI Copilot 2.0 Incident Reasoning")
async def copilot_reason(
    payload: CopilotReasonRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Executes multi-step analyst reasoning with prompt injection defense and human-gated remediation."""
    tenant_id = context.tenant_id or "default-tenant"
    user_id = context.user_id or "SOC_ANALYST"
    return await AICopilotV2Service.chat_reason(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        prompt=payload.prompt,
        incident_id=payload.incident_id
    )
