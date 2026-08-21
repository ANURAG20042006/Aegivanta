"""
backend/app/api/v1/attack_surface.py
====================================
Phase 31 Attack Surface Management (ASM), Threat Exposure Management (CTEM) & External Recon API Router.
Exposes:
- ASM & CTEM Exposure Scorecard Summary
- External Asset Inventory & Exposed Ports Map
- Dangling DNS & Subdomain Takeover Vulnerability Audits
- Dark Web Credential Breach Intelligence
- Brand Impersonation & Typosquatting Alerts
- Gartner 5-Stage CTEM Prioritized Exposures
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.external_recon_service import ExternalReconService
from backend.app.services.ctem_prioritization_service import CTEMPrioritizationService
from backend.app.services.darkweb_brand_monitor_service import DarkWebBrandMonitorService
from backend.app.services.asm_posture_service import ASMPostureService

router = APIRouter(prefix="/attack-surface", tags=["Phase 31 - Attack Surface Management & CTEM"])


# ==================== Request Payloads ====================

class DiscoverDomainRequest(BaseModel):
    domain_name: str = Field(..., example="staging-api.aegivanta.io")
    cloud_provider: str = Field(default="AWS", example="AWS")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get Attack Surface & CTEM Exposure Scorecard")
async def get_asm_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates consolidated ASM posture score and perimeter exposure metrics."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ASMPostureService.get_summary(db=db, tenant_id=tenant_id)


# External Assets
@router.get("/assets", summary="List Discovered External Assets")
async def list_external_assets(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists discovered external perimeter assets and open ports."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ExternalReconService.list_external_assets(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/assets/discover", summary="Discover and Enroll External Domain")
async def discover_external_domain(
    req: DiscoverDomainRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Enrolls a new external domain or IP into the asset inventory."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ExternalReconService.discover_new_domain(
        db=db,
        tenant_id=tenant_id,
        domain_name=req.domain_name,
        cloud_provider=req.cloud_provider
    )


# Dangling DNS
@router.get("/dangling-dns", summary="List Dangling DNS Takeover Vulnerabilities")
async def list_dangling_dns(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists dangling DNS records susceptible to subdomain takeover."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ExternalReconService.list_dangling_dns(db=db, tenant_id=tenant_id, limit=limit)


# Dark Web Credentials
@router.get("/darkweb/credentials", summary="List Dark Web Leaked Credentials")
async def list_darkweb_credentials(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists compromised corporate credentials found on the dark web."""
    tenant_id = context.tenant_id or "default-tenant"
    return await DarkWebBrandMonitorService.list_credential_leaks(db=db, tenant_id=tenant_id, limit=limit)


# Brand Protection
@router.get("/brand/typosquats", summary="List Typosquatted Domains & Phishing Lures")
async def list_brand_typosquats(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists typosquatted lookalike domains impersonating the brand."""
    tenant_id = context.tenant_id or "default-tenant"
    return await DarkWebBrandMonitorService.list_brand_alerts(db=db, tenant_id=tenant_id, limit=limit)


# CTEM Prioritization
@router.get("/ctem/prioritized-exposures", summary="Get CTEM Prioritized Exposures")
async def get_ctem_prioritized_exposures(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Returns prioritized external exposures sorted by CTEM mobilization urgency."""
    tenant_id = context.tenant_id or "default-tenant"
    return await CTEMPrioritizationService.list_prioritized_exposures(db=db, tenant_id=tenant_id)
