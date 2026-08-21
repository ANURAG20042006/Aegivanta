"""
backend/app/models/cloud_security.py
====================================
Phase 21 & Phase 27 Cloud-Native Application Protection Platform (CNAPP) Models.
Covers Multi-Cloud Account Onboarding, Cloud Asset Inventory, CSPM Misconfigurations,
Container Vulnerability Scans & SBOM, CWPP Workload Threat Findings, Serverless Risks,
KSPM Cluster Governance, CIEM Identity Risks, and Attack Path Graph Models.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database import Base


class CloudAccount(Base):
    """
    Multi-Cloud Onboarding & Account Credentials Registry.
    Supports AWS (AssumeRole / IAM), Azure (Service Principal), GCP (Service Account), and K8s.
    Sensitive credentials are encrypted with tenant-scoped cryptographic keys.
    """
    __tablename__ = "cloud_accounts"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    provider: Mapped[str] = mapped_column(String(30), nullable=False, index=True)  # AWS, AZURE, GCP, KUBERNETES
    account_name: Mapped[str] = mapped_column(String(150), nullable=False)
    account_identifier: Mapped[str] = mapped_column(String(150), nullable=False, index=True)  # AWS Account ID / Azure Sub ID / GCP Project ID / Cluster Name
    environment: Mapped[str] = mapped_column(String(50), default="PRODUCTION", nullable=False)  # PRODUCTION, STAGING, DEVELOPMENT

    auth_type: Mapped[str] = mapped_column(String(50), default="ASSUME_ROLE", nullable=False)  # ASSUME_ROLE, SERVICE_PRINCIPAL, SERVICE_ACCOUNT_KEY, KUBECONFIG
    encrypted_credentials: Mapped[str] = mapped_column(Text, nullable=False)  # Fernet-encrypted JSON payload

    sync_status: Mapped[str] = mapped_column(String(30), default="SYNCED", nullable=False)  # SYNCED, PENDING, ERROR, DISCONNECTED
    health_status: Mapped[str] = mapped_column(String(30), default="HEALTHY", nullable=False)
    discovered_assets_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_findings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class CloudAsset(Base):
    """
    Multi-Cloud & Kubernetes Asset Inventory.
    Tracks VMs, Containers, Databases, S3/GCS Buckets, Load Balancers, and IAM Identities.
    """
    __tablename__ = "cloud_assets"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    provider: Mapped[str] = mapped_column(String(30), nullable=False, index=True)  # AWS, GCP, AZURE, KUBERNETES
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # VM, CONTAINER, K8S_POD, K8S_DEPLOYMENT, DATABASE, STORAGE_BUCKET, LOAD_BALANCER, IAM_ROLE, IAM_USER, SERVERLESS_FUNCTION
    resource_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    resource_name: Mapped[str] = mapped_column(String(200), nullable=False)
    region: Mapped[str] = mapped_column(String(50), default="us-east-1", nullable=False)
    account_id: Mapped[str] = mapped_column(String(100), default="123456789012", nullable=False)

    exposure_level: Mapped[str] = mapped_column(String(30), default="INTERNAL", nullable=False)  # INTERNAL, PUBLIC_INGRESS, RESTRICTED
    tags: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    configuration: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    risk_score: Mapped[float] = mapped_column(Float, default=20.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class CSPMFinding(Base):
    """
    Cloud Security Posture Management (CSPM) Compliance & Misconfiguration Findings.
    """
    __tablename__ = "cspm_findings"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")
    asset_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    rule_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # STORAGE_SECURITY, NETWORK_EXPOSURE, ENCRYPTION, AUTHENTICATION, IAM_PRIVILEGE, KUBERNETES_WORKLOAD

    compliance_standard: Mapped[str] = mapped_column(String(50), default="CIS_BENCHMARK", nullable=False)
    remediation_guidance: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="OPEN", nullable=False)  # OPEN, SUPPRESSED, RESOLVED

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )


class CloudWorkloadFinding(Base):
    """
    Cloud Workload Protection Platform (CWPP) Runtime Threat & Behavioral Anomaly Findings.
    Detects reverse shells, crypto-mining, namespace breakouts, and suspicious process executions.
    """
    __tablename__ = "cloud_workload_findings"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    workload_type: Mapped[str] = mapped_column(String(30), nullable=False)  # VM, CONTAINER, K8S_POD, SERVERLESS
    workload_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    workload_name: Mapped[str] = mapped_column(String(200), nullable=False)
    host_ip: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    threat_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # REVERSE_SHELL, CRYPTO_MINER, CAPABILITY_ABUSE, SENSITIVE_FILE_ACCESS, ANOMALOUS_OUTBOUND
    severity: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    process_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    command_line: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mitre_attack_technique: Mapped[str] = mapped_column(String(50), default="T1059", nullable=False)

    containment_status: Mapped[str] = mapped_column(String(30), default="DETECTED", nullable=False)  # DETECTED, QUARANTINED, TERMINATED, DISMISSED
    is_contained: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )


class ServerlessFunctionRisk(Base):
    """
    Serverless Security Posture Findings (AWS Lambda, GCP Cloud Functions, Azure Functions).
    Detects excessive wildcard IAM policies, exposed env secrets, unauthenticated public URLs.
    """
    __tablename__ = "serverless_function_risks"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    provider: Mapped[str] = mapped_column(String(30), nullable=False)  # AWS, GCP, AZURE
    function_arn: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    function_name: Mapped[str] = mapped_column(String(150), nullable=False)
    runtime: Mapped[str] = mapped_column(String(50), nullable=False)  # python3.11, nodejs20.x, etc.

    has_public_url: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_unencrypted_env_vars: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_wildcard_iam: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    vulnerable_dependencies_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    risk_score: Mapped[float] = mapped_column(Float, default=25.0, nullable=False)
    remediation_advice: Mapped[str] = mapped_column(Text, nullable=False)

    audited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class KubernetesCluster(Base):
    """
    Kubernetes Security Posture Management (KSPM) Cluster Registry.
    Tracks cluster version, node count, Pod Security Standard compliance, and RBAC posture.
    """
    __tablename__ = "kubernetes_clusters"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    cluster_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    distribution: Mapped[str] = mapped_column(String(50), default="EKS", nullable=False)  # EKS, GKE, AKS, SELF_HOSTED
    k8s_version: Mapped[str] = mapped_column(String(30), default="v1.28.4", nullable=False)
    node_count: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    pod_count: Mapped[int] = mapped_column(Integer, default=42, nullable=False)

    admission_controller_enforced: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    pod_security_standard: Mapped[str] = mapped_column(String(30), default="RESTRICTED", nullable=False)  # PRIVILEGED, BASELINE, RESTRICTED
    privileged_workloads_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    kspm_health_score: Mapped[float] = mapped_column(Float, default=92.0, nullable=False)

    last_audited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class ContainerVulnerabilityScan(Base):
    """
    Container Image Security Scans, CVE Vulnerability Ledger, and SBOM Manifests.
    """
    __tablename__ = "container_vulnerability_scans"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    image_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    image_tag: Mapped[str] = mapped_column(String(100), default="latest", nullable=False)
    image_digest: Mapped[str] = mapped_column(String(100), nullable=False)

    signature_status: Mapped[str] = mapped_column(String(30), default="SIGNED_VALID", nullable=False)  # SIGNED_VALID, UNSIGNED, SIGNATURE_INVALID
    sbom_components_count: Mapped[int] = mapped_column(Integer, default=142, nullable=False)
    sbom_summary: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    critical_cve_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    high_cve_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    medium_cve_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vulnerabilities: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)

    scanned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )


class CloudAttackPath(Base):
    """
    Graph-Synthesized Cloud & Container Attack Paths from Internet Ingress to Critical Assets.
    """
    __tablename__ = "cloud_attack_paths"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    source_entity: Mapped[str] = mapped_column(String(200), nullable=False)
    target_critical_asset: Mapped[str] = mapped_column(String(200), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, default=85.0, nullable=False)
    blast_radius: Mapped[str] = mapped_column(String(30), default="HIGH", nullable=False)

    hop_nodes: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    kill_chain_phase: Mapped[str] = mapped_column(String(50), default="PRIVILEGE_ESCALATION", nullable=False)
    remediation_steps: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class CloudIAMIdentityRisk(Base):
    """
    Cloud Infrastructure Entitlement Management (CIEM) Identity Risk & Escalation Vectors.
    """
    __tablename__ = "cloud_iam_identity_risks"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True, default="default-tenant")

    identity_type: Mapped[str] = mapped_column(String(30), nullable=False)  # IAM_USER, IAM_ROLE, SERVICE_ACCOUNT
    identity_arn: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    is_stale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_activity_days: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    has_admin_privileges: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    excessive_wildcard_permissions: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    privilege_escalation_vectors: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, default=35.0, nullable=False)

    audited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
