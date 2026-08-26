"""
backend/app/api/v1/federated_threat_sharing.py
==============================================
Phase 40 Privacy-Preserving Threat Intelligence & Federated IOC Exchange API Router.
Exposes:
- Federated Privacy & Exchange Posture Scorecard
- Verified Exchange Nodes Registry
- Anonymized Federated Threat Indicators
- Anonymized Indicator Dispatcher
- Homomorphic / Blind Match Encrypted Query Engine
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext, get_enforced_tenant_id
from backend.app.services.federated_exchange_service import FederatedExchangeService
from backend.app.services.differential_privacy_service import DifferentialPrivacyService
from backend.app.services.federated_threat_posture_service import FederatedThreatPostureService

router = APIRouter(prefix="/federated-threat", tags=["Phase 40 - Privacy-Preserving Threat Sharing"])


# ==================== Request Payloads ====================

class ShareIndicatorRequest(BaseModel):
    raw_indicator_value: str = Field(..., example="198.51.100.45")
    threat_classification: str = Field(default="APT_C2_INFRASTRUCTURE", example="APT_C2_INFRASTRUCTURE")
    differential_privacy_epsilon: float = Field(default=0.5, example=0.5)


class BlindMatchRequest(BaseModel):
    target_ioc_query: str = Field(..., example="APT29_COZYBEAR_C2_HOST")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get Federated Threat Sharing Posture Scorecard")
async def get_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates consolidated federated sharing score and metrics."""
    tenant_id = get_enforced_tenant_id(context)
    return await FederatedThreatPostureService.get_summary(db=db, tenant_id=tenant_id)


# Nodes
@router.get("/nodes", summary="List Verified Federated Exchange Peer Nodes")
async def list_nodes(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active peer federated exchange nodes."""
    tenant_id = get_enforced_tenant_id(context)
    return await FederatedExchangeService.list_nodes(db=db, tenant_id=tenant_id, limit=limit)


# Indicators
@router.get("/indicators", summary="List Anonymized Federated Threat Indicators")
async def list_indicators(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists anonymized federated threat indicators."""
    tenant_id = get_enforced_tenant_id(context)
    return await FederatedExchangeService.list_indicators(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/indicators/share", summary="Anonymize and Share Threat Indicator to Federated Mesh")
async def share_indicator(
    req: ShareIndicatorRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Anonymizes and shares a threat indicator across the federated mesh."""
    tenant_id = get_enforced_tenant_id(context)
    return await FederatedExchangeService.share_indicator(
        db=db,
        tenant_id=tenant_id,
        raw_indicator_value=req.raw_indicator_value,
        threat_classification=req.threat_classification,
        differential_privacy_epsilon=req.differential_privacy_epsilon
    )


# Homomorphic Blind Matching
@router.post("/blind-match", summary="Execute Homomorphic Blind Match Query")
async def execute_blind_match(
    req: BlindMatchRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Executes encrypted homomorphic / blind hash matching against federated indicators."""
    tenant_id = get_enforced_tenant_id(context)
    return await DifferentialPrivacyService.execute_blind_match(
        db=db,
        tenant_id=tenant_id,
        target_ioc_query=req.target_ioc_query
    )
