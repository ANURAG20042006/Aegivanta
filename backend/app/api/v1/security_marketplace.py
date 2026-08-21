"""
backend/app/api/v1/security_marketplace.py
==========================================
Phase 44 Security Marketplace & Ecosystem Package Manager API Router.
Exposes:
- Marketplace Posture Scorecard
- Curated Package Catalog Search
- Sandboxed Package Installation & Hot-Reloading
- Package Publishing & Signing Studio
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.marketplace_catalog_service import MarketplaceCatalogService
from backend.app.services.package_installer_service import PackageInstallerService
from backend.app.services.marketplace_posture_service import MarketplacePostureService

router = APIRouter(prefix="/marketplace", tags=["Phase 44 - Security Marketplace & Ecosystem"])


# ==================== Request Payloads ====================

class InstallPackageRequest(BaseModel):
    package_id: str = Field(..., example="pkg-123")
    package_name: str = Field(..., example="CrowdStrike Falcon XDR Stream Ingester")
    version: str = Field(default="1.0.0", example="2.4.0")


class UninstallPackageRequest(BaseModel):
    installed_id: str = Field(..., example="ext-456")


class PublishPackageRequest(BaseModel):
    package_name: str = Field(..., example="Autonomous Kubernetes Pod Quarantine Playbook")
    package_type: str = Field(default="SOAR_PLAYBOOK", example="SOAR_PLAYBOOK")
    version: str = Field(default="1.0.0", example="1.0.0")
    author: str = Field(default="Enterprise DevSecOps", example="Enterprise DevSecOps")


# ==================== Endpoints ====================

@router.get("/summary", summary="Get Security Marketplace Posture Scorecard")
async def get_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates consolidated security marketplace scorecard metrics."""
    tenant_id = context.tenant_id or "default-tenant"
    return await MarketplacePostureService.get_summary(db=db, tenant_id=tenant_id)


# Catalog
@router.get("/packages", summary="List Curated Marketplace Packages")
async def list_packages(
    package_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists curated marketplace extensions with verified signatures."""
    return await MarketplaceCatalogService.list_packages(db=db, package_type=package_type, limit=limit)


@router.post("/publish", summary="Publish New Security Extension Package")
async def publish_package(
    req: PublishPackageRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Publishes a new security extension package with signed provenance hash."""
    tenant_id = context.tenant_id or "global-catalog"
    return await MarketplaceCatalogService.publish_package(
        db=db,
        tenant_id=tenant_id,
        package_name=req.package_name,
        package_type=req.package_type,
        version=req.version,
        author=req.author
    )


# Installed
@router.get("/installed", summary="List Installed Tenant Extensions")
async def list_installed(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active installed extensions for a tenant."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PackageInstallerService.list_installed(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/install", summary="Install and Hot-Reload Security Extension")
async def install_package(
    req: InstallPackageRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Installs and hot-reloads a package into the tenant's security environment."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PackageInstallerService.install_package(
        db=db,
        tenant_id=tenant_id,
        package_id=req.package_id,
        package_name=req.package_name,
        version=req.version
    )


@router.post("/uninstall", summary="Uninstall and Deactivate Security Extension")
async def uninstall_package(
    req: UninstallPackageRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Uninstalls and deactivates a security extension."""
    tenant_id = context.tenant_id or "default-tenant"
    return await PackageInstallerService.uninstall_package(
        db=db,
        tenant_id=tenant_id,
        installed_id=req.installed_id
    )
