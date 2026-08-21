"""
backend/app/api/v1/cloud_security.py
====================================
Phase 21 & Phase 27 Cloud-Native Application Protection Platform (CNAPP) API Router.
Exposes:
- Multi-Cloud Account Management & Connectors (AWS, Azure, GCP, K8s)
- Unified CNAPP Posture Summary & Scorecard
- Cloud Workload Protection Platform (CWPP) Runtime Threat Detections
- Serverless Security Posture & Function Audits
- Kubernetes Security Posture Management (KSPM) Clusters & Manifest Audits
- Cloud Security Posture Management (CSPM) Compliance & Misconfiguration Scans
- Container Vulnerability Scanning & SBOM Generation
- Cloud Infrastructure Entitlement Management (CIEM) IAM Risk Analysis
- Multi-Cloud Attack Path Graph Synthesizer
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.core.tenant import resolve_tenant_context, TenantContext
from backend.app.services.cloud_account_connector_service import CloudAccountConnectorService
from backend.app.services.cnapp_posture_service import CNAPPPostureService
from backend.app.services.cloud_workload_protection_service import CloudWorkloadProtectionService
from backend.app.services.serverless_security_service import ServerlessSecurityService
from backend.app.services.cloud_asset_inventory_service import CloudAssetInventoryService
from backend.app.services.cspm_rule_engine import CSPMRuleEngine
from backend.app.services.container_security_service import ContainerSecurityService
from backend.app.services.kubernetes_security_service import KubernetesSecurityService
from backend.app.services.cloud_iam_analyzer_service import CloudIAMAnalyzerService
from backend.app.services.cloud_attack_path_service import CloudAttackPathService
from backend.app.observability import metrics

router = APIRouter(prefix="/cloud-security", tags=["CNAPP - Cloud & Container Security"])


# ==================== Request Payloads ====================

class ConnectCloudAccountRequest(BaseModel):
    provider: str = Field(..., example="AWS")
    account_name: str = Field(..., example="AWS-Production-Main")
    account_identifier: str = Field(..., example="123456789012")
    auth_type: str = Field(default="ASSUME_ROLE", example="ASSUME_ROLE")
    credentials: Dict[str, Any] = Field(default_factory=dict, example={"role_arn": "arn:aws:iam::123456789012:role/AegivantaSecurityRole"})
    environment: str = Field(default="PRODUCTION", example="PRODUCTION")


class ContainerScanRequest(BaseModel):
    image_name: str = Field(..., example="aegivanta/backend")
    image_tag: str = Field(default="v27.0.0", example="v27.0.0")
    signature_token: Optional[str] = Field(default="sig_valid_release_key_2026")


class K8sManifestAuditRequest(BaseModel):
    manifest_yaml: str = Field(..., description="Kubernetes YAML manifest content to audit")


class EnrollK8sClusterRequest(BaseModel):
    cluster_name: str = Field(..., example="EKS-Production-Cluster-02")
    distribution: str = Field(default="EKS", example="EKS")
    k8s_version: str = Field(default="v1.28.4", example="v1.28.4")
    node_count: int = Field(default=8, ge=1)
    pod_security_standard: str = Field(default="RESTRICTED", example="RESTRICTED")


class SimulateCWPPThreatRequest(BaseModel):
    workload_type: str = Field(default="K8S_POD", example="K8S_POD")
    threat_type: str = Field(default="REVERSE_SHELL", example="REVERSE_SHELL")
    target_name: str = Field(default="web-frontend-pod-01", example="web-frontend-pod-01")


class AuditServerlessFunctionRequest(BaseModel):
    provider: str = Field(default="AWS", example="AWS")
    function_name: str = Field(..., example="payment-processor")
    runtime: str = Field(default="python3.11", example="python3.11")
    has_public_url: bool = Field(default=False)
    env_vars_plaintext: List[str] = Field(default_factory=list)
    iam_permissions: List[str] = Field(default_factory=list)


# ==================== Multi-Cloud Accounts & CNAPP Posture ====================

@router.get("/cnapp/summary", summary="Get Consolidated CNAPP Posture Scorecard")
async def get_cnapp_summary(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Calculates multi-pillar CNAPP security posture score and pillar breakdowns."""
    tenant_id = context.tenant_id or "default-tenant"
    return await CNAPPPostureService.get_cnapp_summary(db=db, tenant_id=tenant_id)


@router.get("/accounts", summary="List Connected Multi-Cloud Accounts")
async def list_cloud_accounts(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists connected cloud accounts across AWS, Azure, GCP, and Kubernetes."""
    tenant_id = context.tenant_id or "default-tenant"
    return await CloudAccountConnectorService.list_accounts(db=db, tenant_id=tenant_id)


@router.post("/accounts", summary="Connect Multi-Cloud Account")
async def connect_cloud_account(
    req: ConnectCloudAccountRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Onboards a cloud account with encrypted credentials and triggers initial inventory sync."""
    tenant_id = context.tenant_id or "default-tenant"
    account = await CloudAccountConnectorService.connect_account(
        db=db,
        tenant_id=tenant_id,
        provider=req.provider,
        account_name=req.account_name,
        account_identifier=req.account_identifier,
        auth_type=req.auth_type,
        credentials=req.credentials,
        environment=req.environment
    )
    return {
        "id": account.id,
        "provider": account.provider,
        "account_name": account.account_name,
        "sync_status": account.sync_status,
        "created_at": account.created_at.isoformat()
    }


@router.post("/accounts/{id}/sync", summary="Trigger Live Multi-Cloud Account Discovery Sync")
async def sync_cloud_account(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Executes on-demand asset discovery and configuration sync for the cloud account."""
    tenant_id = context.tenant_id or "default-tenant"
    return await CloudAccountConnectorService.sync_account(db=db, tenant_id=tenant_id, account_id=id)


# ==================== CWPP Workload Threat Defense ====================

@router.get("/cwpp/findings", summary="List CWPP Workload Threat Detections")
async def list_cwpp_findings(
    limit: int = Query(50, ge=1, le=100),
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists active runtime threat detections across VMs, Containers, and Kubernetes Pods."""
    tenant_id = context.tenant_id or "default-tenant"
    return await CloudWorkloadProtectionService.list_findings(db=db, tenant_id=tenant_id, limit=limit)


@router.post("/cwpp/simulate-threat", summary="Simulate CWPP Workload Threat")
async def simulate_cwpp_threat(
    req: SimulateCWPPThreatRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Simulates a synthetic workload runtime attack for validation."""
    tenant_id = context.tenant_id or "default-tenant"
    return await CloudWorkloadProtectionService.simulate_workload_threat(
        db=db,
        tenant_id=tenant_id,
        workload_type=req.workload_type,
        threat_type=req.threat_type,
        target_name=req.target_name
    )


@router.post("/cwpp/contain/{id}", summary="Quarantine / Contain Workload")
async def contain_workload(
    id: str,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Applies governed containment on a compromised workload."""
    tenant_id = context.tenant_id or "default-tenant"
    return await CloudWorkloadProtectionService.contain_workload(db=db, tenant_id=tenant_id, finding_id=id)


# ==================== Serverless Security Posture ====================

@router.get("/serverless/findings", summary="List Serverless Function Risks")
async def list_serverless_findings(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists serverless function misconfigurations and overprivileged IAM execution roles."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ServerlessSecurityService.list_findings(db=db, tenant_id=tenant_id)


@router.post("/serverless/audit", summary="Audit Serverless Function Configuration")
async def audit_serverless_function(
    req: AuditServerlessFunctionRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Audits serverless function for public URLs, unencrypted secrets, and wildcard IAM."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ServerlessSecurityService.audit_function(
        db=db,
        tenant_id=tenant_id,
        provider=req.provider,
        function_name=req.function_name,
        runtime=req.runtime,
        has_public_url=req.has_public_url,
        env_vars_plaintext=req.env_vars_plaintext,
        iam_permissions=req.iam_permissions
    )


# ==================== KSPM Kubernetes Clusters ====================

@router.get("/k8s/clusters", summary="List Kubernetes Clusters & KSPM Posture")
async def list_k8s_clusters(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists registered Kubernetes clusters with Pod Security Standard compliance."""
    tenant_id = context.tenant_id or "default-tenant"
    return await KubernetesSecurityService.list_clusters(db=db, tenant_id=tenant_id)


@router.post("/k8s/clusters/enroll", summary="Enroll Kubernetes Cluster into KSPM")
async def enroll_k8s_cluster(
    req: EnrollK8sClusterRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Enrolls a Kubernetes cluster for continuous manifest and RBAC auditing."""
    tenant_id = context.tenant_id or "default-tenant"
    cluster = await KubernetesSecurityService.enroll_cluster(
        db=db,
        tenant_id=tenant_id,
        cluster_name=req.cluster_name,
        distribution=req.distribution,
        k8s_version=req.k8s_version,
        node_count=req.node_count,
        pod_security_standard=req.pod_security_standard
    )
    return {
        "id": cluster.id,
        "cluster_name": cluster.cluster_name,
        "kspm_health_score": cluster.kspm_health_score,
        "pod_security_standard": cluster.pod_security_standard
    }


# ==================== Existing Asset, CSPM & Container APIs ====================

@router.get("/inventory", summary="Get Cloud Asset Inventory")
async def get_cloud_inventory(
    provider: Optional[str] = None,
    asset_type: Optional[str] = None,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists cloud and container assets across AWS, GCP, Azure, and Kubernetes."""
    tenant_id = context.tenant_id or "default-tenant"
    assets = await CloudAssetInventoryService.list_assets(
        db=db,
        tenant_id=tenant_id,
        provider=provider,
        asset_type=asset_type
    )
    metrics.aegivanta_cloud_assets_total.set(len(assets))
    return assets


@router.post("/cspm/scan", summary="Run CSPM Compliance Scan")
async def run_cspm_scan(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Executes CSPM benchmark and misconfiguration audit across cloud assets."""
    tenant_id = context.tenant_id or "default-tenant"
    summary = await CSPMRuleEngine.run_full_cspm_scan(db=db, tenant_id=tenant_id)
    metrics.aegivanta_cspm_findings_total.set(summary["total_open_findings"])
    return summary


@router.get("/cspm/findings", summary="Get CSPM Findings")
async def get_cspm_findings(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves open CSPM compliance and misconfiguration findings."""
    tenant_id = context.tenant_id or "default-tenant"
    return await CSPMRuleEngine.list_findings(db=db, tenant_id=tenant_id)


@router.post("/containers/scan", summary="Scan Container Image")
async def scan_container_image(
    req: ContainerScanRequest,
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Scans container image for CVEs, creates SBOM catalog, and verifies signatures."""
    tenant_id = context.tenant_id or "default-tenant"
    res = await ContainerSecurityService.scan_container_image(
        db=db,
        tenant_id=tenant_id,
        image_name=req.image_name,
        image_tag=req.image_tag,
        signature_token=req.signature_token
    )
    metrics.aegivanta_container_images_scanned_total.inc()
    return res


@router.get("/containers/scans", summary="List Container Scans")
async def list_container_scans(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Lists recent container vulnerability and SBOM scans."""
    tenant_id = context.tenant_id or "default-tenant"
    return await ContainerSecurityService.list_image_scans(db=db, tenant_id=tenant_id)


@router.post("/k8s/audit-manifest", summary="Audit Kubernetes Manifest")
async def audit_k8s_manifest(
    req: K8sManifestAuditRequest
):
    """Audits Kubernetes manifest for privileged containers, host sharing, and plain secrets."""
    res = KubernetesSecurityService.audit_manifest_content(req.manifest_yaml)
    if res["violations_count"] > 0:
        metrics.aegivanta_k8s_workload_violations_total.inc(res["violations_count"])
    return res


@router.get("/iam/analysis", summary="Get Cloud IAM Entitlement Analysis")
async def get_cloud_iam_analysis(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves Cloud IAM (CIEM) entitlement risk analysis and privilege escalation paths."""
    tenant_id = context.tenant_id or "default-tenant"
    res = await CloudIAMAnalyzerService.get_iam_risk_analysis(db=db, tenant_id=tenant_id)
    metrics.aegivanta_cloud_iam_privilege_escalation_paths_total.set(res["privilege_escalation_vectors_count"])
    return res


@router.get("/attack-paths", summary="Get Cloud Attack Paths")
async def get_cloud_attack_paths(
    context: TenantContext = Depends(resolve_tenant_context),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves explainable graph-synthesized cloud attack paths."""
    tenant_id = context.tenant_id or "default-tenant"
    return await CloudAttackPathService.list_attack_paths(db=db, tenant_id=tenant_id)
