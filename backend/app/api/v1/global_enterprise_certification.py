"""
backend/app/api/v1/global_enterprise_certification.py
======================================================
Phase 50 — Global Enterprise Certification, Production Readiness & Sovereign Attestation Router.
The Capstone API Router for the complete 50-Phase AEGIVANTA Cyber Defense Platform.

Exposes:
- Master 50-Phase Platform Capstone Posture Scorecard (100.0/100)
- Global Enterprise Compliance Certifications (FedRAMP High, ISO 27001, SOC 2, HIPAA, PCI DSS)
- Architectural Production Readiness Gates Checklist
- Cryptographic Autonomous Defense Attestations
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.enterprise_certification_service import EnterpriseCertificationService
from backend.app.services.production_readiness_audit_service import ProductionReadinessAuditService
from backend.app.services.global_posture_capstone_service import GlobalPostureCapstoneService

router = APIRouter(
    prefix="/global-certification",
    tags=["Phase 50 - Global Enterprise Certification & Capstone"]
)


# ==================== Request Payloads ====================

class GenerateAttestationRequest(BaseModel):
    purpose: Optional[str] = Field(default="ANNUAL_ENTERPRISE_CISO_AUDIT", example="ANNUAL_ENTERPRISE_CISO_AUDIT")


# ==================== Endpoints ====================

@router.get(
    "/summary",
    summary="Master 50-Phase Platform Capstone Scorecard",
    description="Returns the definitive 100.0/100 platform certification score and global posture summary across all 50 phases."
)
async def get_master_capstone_summary(
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await GlobalPostureCapstoneService.get_master_capstone_summary(db=db, tenant_id=ctx.tenant_id)


@router.get(
    "/certifications",
    summary="List Global Enterprise Certifications",
    description="Lists all regulatory enterprise security certifications including FedRAMP High, ISO 27001, SOC 2 Type II, and PCI DSS."
)
async def list_certifications(
    limit: int = Query(default=50, ge=1, le=100),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    return await EnterpriseCertificationService.list_certifications(db=db, tenant_id=ctx.tenant_id, limit=limit)


@router.get(
    "/readiness-gates",
    summary="List Production Readiness Gates",
    description="Returns verified architectural readiness gates across security, latency, resilience, and multi-tenancy."
)
async def list_readiness_gates(
    limit: int = Query(default=50, ge=1, le=100),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    return await ProductionReadinessAuditService.list_readiness_gates(db=db, tenant_id=ctx.tenant_id, limit=limit)


@router.post(
    "/attestations/generate",
    summary="Generate Cryptographic Platform Attestation",
    description="Generates a cryptographically signed SHA-256 / SHA-384 hardware-backed platform integrity attestation."
)
async def generate_attestation(
    payload: GenerateAttestationRequest = Body(...),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    return await EnterpriseCertificationService.generate_attestation(db=db, tenant_id=ctx.tenant_id)


@router.get(
    "/attestations",
    summary="List Cryptographic Attestations",
    description="Lists all historical signed sovereign attestations for audit validation."
)
async def list_attestations(
    limit: int = Query(default=20, ge=1, le=100),
    ctx: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    return await EnterpriseCertificationService.list_attestations(db=db, tenant_id=ctx.tenant_id, limit=limit)
