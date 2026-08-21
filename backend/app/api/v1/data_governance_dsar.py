"""
backend/app/api/v1/data_governance_dsar.py
==========================================
Phase 43 Enterprise Data Governance, Lineage, Legal Hold & DSAR Privacy API Router.
Exposes:
- Governance & DSAR Posture Scorecard
- Telemetry Lineage & Provenance Stages
- Forensic Legal Hold Custody Vault
- GDPR / CCPA DSAR Privacy Workflows
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.data_lineage_service import DataLineageService
from backend.app.services.legal_hold_service import LegalHoldService
from backend.app.services.dsar_workflow_service import DSARWorkflowService
from backend.app.services.data_governance_posture_service import DataGovernancePostureService

router = APIRouter(prefix="/governance-dsar", tags=["Phase 43 - Enterprise Data Governance & DSAR"])


# ==================== Request Payloads ====================

class CreateLegalHoldRequest(BaseModel):
    matter_reference: str = Field(..., example="MATTER-2026-SEC-INVESTIGATION-04")
    custodian_name: str = Field(..., example="Chief Legal Officer")
    scope_pattern: str = Field(default="CASE_FORENSICS_*", example="CASE_FORENSICS_*")


class CreateDSARRequest(BaseModel):
    requester_email: str = Field(..., example="user@enterprise.com")
    request_type: str = Field(default="RIGHT_OF_ACCESS_EXPORT", example="RIGHT_OF_ACCESS_EXPORT")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get Data Governance & DSAR Posture Scorecard")
async def get_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates consolidated data governance metrics and scorecard."""
    tenant_id = context.tenant_id or "default-tenant"
    return await DataGovernancePostureService.get_summary(db=db, tenant_id=tenant_id)


# Lineage
@router.get("/lineage", summary="List Data Lineage & Provenance Stages")
async def list_lineage(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active data lineage records across processing stages."""
    tenant_id = context.tenant_id or "default-tenant"
    return await DataLineageService.list_lineage(db=db, tenant_id=tenant_id, limit=limit)


# Legal Holds
@router.get("/legal-holds", summary="List Forensic Legal Hold Custody Orders")
async def list_holds(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active and historical legal hold orders."""
    tenant_id = context.tenant_id or "default-tenant"
    return await LegalHoldService.list_holds(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/legal-holds", summary="Issue New Forensic Legal Hold Order")
async def create_hold(
    req: CreateLegalHoldRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Issues a new forensic legal hold order freezing matching artifacts."""
    tenant_id = context.tenant_id or "default-tenant"
    return await LegalHoldService.create_hold(
        db=db,
        tenant_id=tenant_id,
        matter_reference=req.matter_reference,
        custodian_name=req.custodian_name,
        scope_pattern=req.scope_pattern
    )


# DSAR Requests
@router.get("/requests", summary="List DSAR Privacy Requests")
async def list_requests(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active and completed DSAR privacy requests."""
    tenant_id = context.tenant_id or "default-tenant"
    return await DSARWorkflowService.list_requests(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/requests", summary="Submit and Process New DSAR Privacy Request")
async def create_request(
    req: CreateDSARRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Submits and processes a new DSAR privacy request."""
    tenant_id = context.tenant_id or "default-tenant"
    return await DSARWorkflowService.create_request(
        db=db,
        tenant_id=tenant_id,
        requester_email=req.requester_email,
        request_type=req.request_type
    )
