"""
backend/app/api/v1/supply_chain.py
==================================
Phase 29 Supply Chain Security, SBOM 2.0 & Code-to-Cloud Governance API Router.
Exposes:
- Supply Chain Security & SLSA Level 3 Scorecard Summary
- SBOM 2.0 Component Catalog & CycloneDX / SPDX Export
- OpenVEX Exploitability Statements & CSAF Publishing
- SLSA Level 3 Provenance Attestation Verification
- CI/CD Deployment Security Gatekeeper Policy Evaluation
- High-Entropy Secret Scanner
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.sbom_engine_service import SBOMEngineService
from backend.app.services.vex_engine_service import VEXEngineService
from backend.app.services.slsa_provenance_service import SLSAProvenanceService
from backend.app.services.cicd_gatekeeper_service import CICDGatekeeperService

router = APIRouter(prefix="/supply-chain", tags=["Phase 29 - Supply Chain & SBOM 2.0"])


# ==================== Request Payloads ====================

class GenerateSBOMRequest(BaseModel):
    format_type: str = Field(default="CYCLONEDX_1_5", example="CYCLONEDX_1_5")


class PublishVEXRequest(BaseModel):
    vulnerability_id: str = Field(..., example="CVE-2026-10492")
    product_purl: str = Field(..., example="pkg:npm/jsonwebtoken@9.0.2")
    status: str = Field(default="NOT_AFFECTED", example="NOT_AFFECTED")
    justification: str = Field(..., example="Vulnerable code is not invoked by execution path")
    impact_statement: str = Field(..., example="Application only performs asymmetric RS256 token verification.")


class VerifySLSARequest(BaseModel):
    artifact_digest: str = Field(..., example="sha256:4b91048b29c9a091e48bc894e7710fa929188a8b9e6f8a4e421c97a5b3a16709")
    expected_slsa_level: str = Field(default="SLSA_LEVEL_3", example="SLSA_LEVEL_3")


class EvaluateGateRequest(BaseModel):
    target_environment: str = Field(default="PRODUCTION", example="PRODUCTION")
    critical_cves: int = Field(default=0, ge=0)
    high_cves: int = Field(default=0, ge=0)
    has_slsa_level_3: bool = Field(default=True)
    has_copyleft_license: bool = Field(default=False)
    has_secrets_detected: bool = Field(default=False)


class SecretScanRequest(BaseModel):
    file_content: str = Field(..., description="Source code text to scan for high-entropy secrets")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get Supply Chain & SLSA Scorecard Summary")
async def get_supply_chain_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates unified supply chain posture score and key metrics."""
    tenant_id = context.tenant_id or "default-tenant"
    return await CICDGatekeeperService.get_supply_chain_summary(db=db, tenant_id=tenant_id)


# SBOM 2.0
@router.get("/sbom/components", summary="List SBOM Components")
async def list_sbom_components(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists SBOM dependency components and license flags."""
    tenant_id = context.tenant_id or "default-tenant"
    return await SBOMEngineService.list_components(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/sbom/generate", summary="Generate CycloneDX / SPDX SBOM Export")
async def generate_sbom_export(
    req: GenerateSBOMRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Generates standard CycloneDX 1.5 or SPDX 2.3 SBOM manifest."""
    tenant_id = context.tenant_id or "default-tenant"
    return await SBOMEngineService.generate_sbom_export(db=db, tenant_id=tenant_id, format_type=req.format_type)


# OpenVEX
@router.get("/vex/statements", summary="List OpenVEX Statements")
async def list_vex_statements(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists OpenVEX exploitability statements."""
    tenant_id = context.tenant_id or "default-tenant"
    return await VEXEngineService.list_statements(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/vex/publish", summary="Publish OpenVEX Statement")
async def publish_vex_statement(
    req: PublishVEXRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Publishes an OpenVEX exploitability statement."""
    tenant_id = context.tenant_id or "default-tenant"
    stmt = await VEXEngineService.publish_statement(
        db=db,
        tenant_id=tenant_id,
        vulnerability_id=req.vulnerability_id,
        product_purl=req.product_purl,
        status=req.status,
        justification=req.justification,
        impact_statement=req.impact_statement
    )
    return {
        "id": stmt.id,
        "vulnerability_id": stmt.vulnerability_id,
        "status": stmt.status,
        "published_at": stmt.published_at.isoformat()
    }


@router.get("/vex/export", summary="Export OpenVEX Document")
async def export_openvex_document(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Exports compliant OpenVEX document."""
    tenant_id = context.tenant_id or "default-tenant"
    return await VEXEngineService.export_openvex_json(db=db, tenant_id=tenant_id)


# SLSA Provenance
@router.get("/slsa/attestations", summary="List SLSA Attestations")
async def list_slsa_attestations(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists SLSA Level 3 provenance build attestations."""
    tenant_id = context.tenant_id or "default-tenant"
    return await SLSAProvenanceService.list_attestations(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/slsa/verify", summary="Verify SLSA Provenance Attestation")
async def verify_slsa_provenance(
    req: VerifySLSARequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Validates SLSA provenance signature and builder isolation for an artifact."""
    tenant_id = context.tenant_id or "default-tenant"
    return await SLSAProvenanceService.verify_provenance(
        db=db,
        tenant_id=tenant_id,
        artifact_digest=req.artifact_digest,
        expected_slsa_level=req.expected_slsa_level
    )


# CI/CD Gates & Secrets
@router.get("/gates", summary="List CI/CD Pipeline Gates")
async def list_pipeline_gates(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists CI/CD security gatekeeper policies."""
    tenant_id = context.tenant_id or "default-tenant"
    return await CICDGatekeeperService.list_gates(db=db, tenant_id=tenant_id)


@router.post("/gates/evaluate", summary="Evaluate Pipeline Deployment Gate")
async def evaluate_pipeline_gate(
    req: EvaluateGateRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Evaluates CI/CD deployment against active gatekeeper policy."""
    tenant_id = context.tenant_id or "default-tenant"
    return await CICDGatekeeperService.evaluate_pipeline_gate(
        db=db,
        tenant_id=tenant_id,
        target_environment=req.target_environment,
        critical_cves=req.critical_cves,
        high_cves=req.high_cves,
        has_slsa_level_3=req.has_slsa_level_3,
        has_copyleft_license=req.has_copyleft_license,
        has_secrets_detected=req.has_secrets_detected
    )


@router.post("/secrets/scan", summary="Scan Code for Secrets & High-Entropy Tokens")
async def scan_code_secrets(
    req: SecretScanRequest
):
    """Scans code text for hardcoded API keys, private keys, and high-entropy secrets."""
    return CICDGatekeeperService.scan_content_for_secrets(req.file_content)
