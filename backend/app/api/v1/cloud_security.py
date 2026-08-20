"""
backend/app/api/v1/cloud_security.py
====================================
Phase 21 Cloud & Container Security API Router.
Exposes CSPM, Container Scans, K8s Audits, CIEM IAM Risk, and Attack Path Graph endpoints.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.services.cloud_asset_inventory_service import CloudAssetInventoryService
from backend.app.services.cspm_rule_engine import CSPMRuleEngine
from backend.app.services.container_security_service import ContainerSecurityService
from backend.app.services.kubernetes_security_service import KubernetesSecurityService
from backend.app.services.cloud_iam_analyzer_service import CloudIAMAnalyzerService
from backend.app.services.cloud_attack_path_service import CloudAttackPathService
from backend.app.observability import metrics

router = APIRouter(prefix="/cloud-security", tags=["Phase 21 - Cloud & Container Security"])


class ContainerScanRequest(BaseModel):
    image_name: str = Field(..., example="aegivanta/backend")
    image_tag: str = Field(default="v21.0.0", example="v21.0.0")
    signature_token: Optional[str] = Field(default="sig_valid_release_key_2026")


class K8sManifestAuditRequest(BaseModel):
    manifest_yaml: str = Field(..., description="Kubernetes YAML manifest content to audit")


@router.get("/inventory")
async def get_cloud_inventory(
    provider: Optional[str] = None,
    asset_type: Optional[str] = None,
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Lists cloud and container assets across AWS, GCP, Azure, and Kubernetes."""
    assets = await CloudAssetInventoryService.list_assets(
        db=db,
        tenant_id=tenant_id,
        provider=provider,
        asset_type=asset_type
    )
    metrics.aegivanta_cloud_assets_total.set(len(assets))
    return assets


@router.post("/cspm/scan")
async def run_cspm_scan(
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Executes CSPM benchmark and misconfiguration audit across cloud assets."""
    summary = await CSPMRuleEngine.run_full_cspm_scan(db=db, tenant_id=tenant_id)
    metrics.aegivanta_cspm_findings_total.set(summary["total_open_findings"])
    return summary


@router.get("/cspm/findings")
async def get_cspm_findings(
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Retrieves open CSPM compliance and misconfiguration findings."""
    return await CSPMRuleEngine.list_findings(db=db, tenant_id=tenant_id)


@router.post("/containers/scan")
async def scan_container_image(
    req: ContainerScanRequest,
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Scans container image for CVEs, creates SBOM catalog, and verifies signatures."""
    res = await ContainerSecurityService.scan_container_image(
        db=db,
        tenant_id=tenant_id,
        image_name=req.image_name,
        image_tag=req.image_tag,
        signature_token=req.signature_token
    )
    metrics.aegivanta_container_images_scanned_total.inc()
    return res


@router.get("/containers/scans")
async def list_container_scans(
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Lists recent container vulnerability and SBOM scans."""
    return await ContainerSecurityService.list_image_scans(db=db, tenant_id=tenant_id)


@router.post("/k8s/audit-manifest")
async def audit_k8s_manifest(
    req: K8sManifestAuditRequest
):
    """Audits Kubernetes manifest for privileged containers, host sharing, and plain secrets."""
    res = KubernetesSecurityService.audit_manifest_content(req.manifest_yaml)
    if res["violations_count"] > 0:
        metrics.aegivanta_k8s_workload_violations_total.inc(res["violations_count"])
    return res


@router.get("/iam/analysis")
async def get_cloud_iam_analysis(
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Retrieves Cloud IAM (CIEM) entitlement risk analysis and privilege escalation paths."""
    res = await CloudIAMAnalyzerService.get_iam_risk_analysis(db=db, tenant_id=tenant_id)
    metrics.aegivanta_cloud_iam_privilege_escalation_paths_total.set(res["privilege_escalation_vectors_count"])
    return res


@router.get("/attack-paths")
async def get_cloud_attack_paths(
    tenant_id: str = "default-tenant",
    db: AsyncSession = Depends(get_db)
):
    """Retrieves explainable graph-synthesized cloud attack paths."""
    return await CloudAttackPathService.list_attack_paths(db=db, tenant_id=tenant_id)
