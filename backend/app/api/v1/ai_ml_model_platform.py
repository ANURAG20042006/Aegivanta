"""
backend/app/api/v1/ai_ml_model_platform.py
===========================================
Phase 48 — Global AI/ML Model Platform, Registry, Drift Monitoring & Adversarial Defenses Router.
Exposes:
- AI/ML Model Platform Posture Scorecard
- Versioned Model Registry Management & Champion Selection
- Statistical Model Drift Monitoring & Alerting
- Adversarial Attack Detection, Defenses & Dry-Run Simulator
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.ml_model_platform_service import MLModelPlatformService
from backend.app.services.drift_monitoring_service import DriftMonitoringService
from backend.app.services.adversarial_defense_service import AdversarialDefenseService

router = APIRouter(
    prefix="/ml-platform",
    tags=["Phase 48 - Global AI/ML Model Platform"]
)


# ==================== Request Payloads ====================

class RegisterModelRequest(BaseModel):
    model_name: str = Field(..., example="CatBoost-ThreatClassifier")
    model_version: str = Field(..., example="v3.3.0")
    model_type: str = Field(..., example="GRADIENT_BOOSTING")
    model_family: str = Field(..., example="THREAT_CLASSIFICATION")
    framework: str = Field(..., example="catboost")
    accuracy: Optional[float] = Field(default=None, example=0.9975)
    f1_score: Optional[float] = Field(default=None, example=0.9972)
    precision_score: Optional[float] = Field(default=None, example=0.9970)
    recall_score: Optional[float] = Field(default=None, example=0.9974)
    roc_auc: Optional[float] = Field(default=None, example=0.9996)
    tags: Optional[List[str]] = Field(default_factory=list, example=["production", "threat-detection"])
    hyperparameters: Optional[Dict[str, Any]] = Field(default_factory=dict, example={"iterations": 1000, "depth": 6})


class SimulateDefenseRequest(BaseModel):
    model_id: str = Field(..., example="cat-001")
    attack_type: str = Field(..., example="EVASION")
    attack_payload: Dict[str, Any] = Field(default_factory=dict, example={"technique": "feature_perturbation", "epsilon": 0.05})


# ==================== Endpoints ====================

@router.get(
    "/summary",
    summary="AI/ML Model Platform Posture Scorecard",
    description="Returns aggregate posture metrics across model registry, active champions, drift watches, and adversarial defenses."
)
async def get_platform_summary(
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await MLModelPlatformService.get_platform_summary(db=db, tenant_id=ctx.tenant_id)


@router.get(
    "/models",
    summary="List Registered ML Models",
    description="Lists all enterprise ML models in the registry with versioning, performance metrics, and deployment status."
)
async def list_models(
    limit: int = Query(default=50, ge=1, le=100),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    return await MLModelPlatformService.list_models(db=db, tenant_id=ctx.tenant_id, limit=limit)


@router.get(
    "/models/champion",
    summary="Get Production Champion Model",
    description="Returns metadata, metrics, and serving endpoint for the active production champion model."
)
async def get_champion_model(
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    return await MLModelPlatformService.get_champion_model(db=db, tenant_id=ctx.tenant_id)


@router.post(
    "/models/register",
    summary="Register New ML Model Version",
    description="Registers a new model version into the enterprise model registry."
)
async def register_model(
    payload: RegisterModelRequest = Body(...),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await MLModelPlatformService.register_model(
        db=db,
        tenant_id=ctx.tenant_id,
        model_name=payload.model_name,
        model_version=payload.model_version,
        model_type=payload.model_type,
        model_family=payload.model_family,
        framework=payload.framework,
        accuracy=payload.accuracy,
        f1_score=payload.f1_score,
        precision_score=payload.precision_score,
        recall_score=payload.recall_score,
        roc_auc=payload.roc_auc,
        tags=payload.tags,
        hyperparameters=payload.hyperparameters,
    )


@router.get(
    "/drift",
    summary="List Statistical Drift Records",
    description="Returns data, concept, and prediction drift monitoring records for all production models."
)
async def list_drift_records(
    limit: int = Query(default=50, ge=1, le=100),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    return await DriftMonitoringService.list_drift_records(db=db, tenant_id=ctx.tenant_id, limit=limit)


@router.get(
    "/drift/summary",
    summary="Model Drift Posture Summary",
    description="Returns overall drift scores, monitored model counts, and auto-retrain pipeline status."
)
async def get_drift_summary(
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await DriftMonitoringService.get_drift_summary(db=db, tenant_id=ctx.tenant_id)


@router.get(
    "/adversarial/events",
    summary="List Adversarial Attack Events",
    description="Lists recent adversarial attacks detected against ML models along with applied defenses."
)
async def list_adversarial_events(
    limit: int = Query(default=50, ge=1, le=100),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    return await AdversarialDefenseService.list_attack_events(db=db, tenant_id=ctx.tenant_id, limit=limit)


@router.get(
    "/adversarial/summary",
    summary="Adversarial Defense Scorecard",
    description="Returns 30-day attack breakdown, block rates, and active defense mechanisms."
)
async def get_adversarial_summary(
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await AdversarialDefenseService.get_defense_summary(db=db, tenant_id=ctx.tenant_id)


@router.post(
    "/adversarial/simulate",
    summary="Simulate Adversarial Defense",
    description="Simulates an adversarial attack (e.g. Evasion, Model Extraction) against a model and verifies defense execution."
)
async def simulate_adversarial_defense(
    payload: SimulateDefenseRequest = Body(...),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await AdversarialDefenseService.simulate_defense(
        db=db,
        tenant_id=ctx.tenant_id,
        model_id=payload.model_id,
        attack_type=payload.attack_type,
        attack_payload=payload.attack_payload,
    )
