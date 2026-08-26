"""
backend/app/api/v1/dlp_security.py
==================================
Phase 35 Data Loss Prevention (DLP) & Cryptographic Tokenization API Router.
Exposes:
- DLP & DSPM Posture Executive Scorecard
- Multi-Channel Inspection Policies & Rule Engine
- Real-Time Payload Inspection & Sanitization Sandbox
- DLP Exfiltration Incident Ledger
- Cryptographic Tokenization & Detokenization Vault
- DSPM Shadow Data Store Discovery
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext, get_enforced_tenant_id
from backend.app.services.dlp_inspection_service import DLPInspectionService
from backend.app.services.tokenization_vault_service import TokenizationVaultService
from backend.app.services.dspm_shadow_data_service import DSPMShadowDataService
from backend.app.services.dlp_posture_service import DLPPostureService

router = APIRouter(prefix="/dlp-security", tags=["Phase 35 - Data Loss Prevention & Tokenization"])


# ==================== Request Payloads ====================

class InspectPayloadRequest(BaseModel):
    payload_text: str = Field(..., example="User order with card 4111-2222-3333-4444 and SSN 123-45-6789")


class TokenizeDataRequest(BaseModel):
    raw_value: str = Field(..., example="4111-9824-7712-1111")
    token_format: str = Field(default="FPE_CREDIT_CARD", example="FPE_CREDIT_CARD")
    authorized_roles: Optional[List[str]] = Field(default=None, example=["admin", "compliance_officer"])


class DetokenizeDataRequest(BaseModel):
    token_identifier: str = Field(..., example="TKN-PCI-4111-9824-7712")
    requestor_role: str = Field(default="admin", example="admin")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get DLP & DSPM Posture Executive Scorecard")
async def get_dlp_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates composite DLP posture score and key data protection metrics."""
    tenant_id = get_enforced_tenant_id(context)
    return await DLPPostureService.get_summary(db=db, tenant_id=tenant_id)


# Inspection Policies
@router.get("/policies", summary="List DLP Inspection Policies")
async def list_dlp_policies(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active sensitive data inspection policies."""
    tenant_id = get_enforced_tenant_id(context)
    return await DLPInspectionService.list_policies(db=db, tenant_id=tenant_id, limit=limit)


# Real-Time Inspection Sandbox
@router.post("/inspect", summary="Inspect & Classify Payload in Sandbox")
async def inspect_payload(
    req: InspectPayloadRequest,
    context: TenantContext = Depends(resolve_tenant_context)
):
    """Inspects raw payload text for PCI, PII, and Secrets, returning sanitized output."""
    return DLPInspectionService.inspect_text_payload(payload_text=req.payload_text)


# Exfiltration Incidents
@router.get("/incidents", summary="List DLP Exfiltration Incidents")
async def list_dlp_incidents(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists intercepted DLP data transmission violations."""
    tenant_id = get_enforced_tenant_id(context)
    return await DLPInspectionService.list_incidents(db=db, tenant_id=tenant_id, limit=limit)


# Tokenization Vault
@router.get("/tokens", summary="List Tokenized Data Vault Records")
async def list_token_vault(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active cryptographic tokenization vault entries."""
    tenant_id = get_enforced_tenant_id(context)
    return await TokenizationVaultService.list_tokens(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/tokens/tokenize", summary="Tokenize Sensitive Data into Surrogate")
async def tokenize_data(
    req: TokenizeDataRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Tokenizes sensitive data into a format-preserving surrogate token."""
    tenant_id = get_enforced_tenant_id(context)
    return await TokenizationVaultService.tokenize_data(
        db=db,
        tenant_id=tenant_id,
        raw_value=req.raw_value,
        token_format=req.token_format,
        authorized_roles=req.authorized_roles
    )


@router.post("/tokens/detokenize", summary="Detokenize Surrogate (RBAC Governed)")
async def detokenize_data(
    req: DetokenizeDataRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Reversibly detokenizes a surrogate token if requestor role is authorized."""
    tenant_id = get_enforced_tenant_id(context)
    return await TokenizationVaultService.detokenize_data(
        db=db,
        tenant_id=tenant_id,
        token_identifier=req.token_identifier,
        requestor_role=req.requestor_role
    )


# Shadow Data & DSPM
@router.get("/shadow-data", summary="List Discovered Shadow Data Stores")
async def list_shadow_data(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists discovered cloud storage buckets and database assets containing sensitive data."""
    tenant_id = get_enforced_tenant_id(context)
    return await DSPMShadowDataService.list_shadow_data_stores(db=db, tenant_id=tenant_id, limit=limit)
