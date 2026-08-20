"""
backend/app/services/cspm_rule_engine.py
========================================
Phase 21 Cloud Security Posture Management (CSPM) Rule Engine.
Evaluates multi-cloud assets against CIS benchmarks and security standards.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.cloud_security import CloudAsset, CSPMFinding
from backend.app.services.cloud_asset_inventory_service import CloudAssetInventoryService

logger = logging.getLogger("Aegivanta.CSPMEngine")


class CSPMRuleEngine:
    """Evaluates multi-cloud asset configurations against security baselines."""

    @classmethod
    async def evaluate_asset_security_posture(cls, asset: CloudAsset) -> List[Dict[str, Any]]:
        """Evaluates a single cloud asset and returns identified misconfiguration findings."""
        findings = []
        cfg = asset.configuration or {}

        # 1. Storage Security Rules
        if asset.asset_type == "STORAGE_BUCKET":
            if cfg.get("public_read") is True or asset.exposure_level == "PUBLIC_INGRESS":
                findings.append({
                    "rule_id": "CSPM-S3-001",
                    "title": "Publicly Accessible Cloud Storage Bucket",
                    "description": f"Bucket {asset.resource_name} allows unrestricted public read access.",
                    "severity": "CRITICAL",
                    "category": "STORAGE_SECURITY",
                    "compliance_standard": "CIS_AWS_BENCHMARK_2.1",
                    "remediation_guidance": "Enable S3 Block Public Access at the bucket and account level immediately."
                })
            if cfg.get("server_side_encryption") is False:
                findings.append({
                    "rule_id": "CSPM-S3-002",
                    "title": "Missing Default Server-Side Encryption",
                    "description": f"Bucket {asset.resource_name} does not enforce KMS or AES-256 encryption-at-rest.",
                    "severity": "HIGH",
                    "category": "ENCRYPTION",
                    "compliance_standard": "CIS_AWS_BENCHMARK_2.2",
                    "remediation_guidance": "Enable default SSE-KMS encryption with customer managed keys."
                })

        # 2. Network Exposure Rules
        if asset.asset_type == "VM":
            open_ports = cfg.get("open_ports", [])
            if 22 in open_ports or 3389 in open_ports:
                findings.append({
                    "rule_id": "CSPM-NET-001",
                    "title": "Management Ports Exposed (SSH/RDP)",
                    "description": f"VM {asset.resource_name} exposes administrative ports (22/3389) without bastion gateway restriction.",
                    "severity": "HIGH",
                    "category": "NETWORK_EXPOSURE",
                    "compliance_standard": "CIS_AWS_BENCHMARK_4.1",
                    "remediation_guidance": "Restrict port 22 and 3389 to internal VPN subnets or AWS Systems Manager Session Manager."
                })

        # 3. Database Security Rules
        if asset.asset_type == "DATABASE":
            if cfg.get("publicly_accessible") is True:
                findings.append({
                    "rule_id": "CSPM-DB-001",
                    "title": "Database Publicly Reachable",
                    "description": f"Database {asset.resource_name} is configured with public IP accessibility.",
                    "severity": "CRITICAL",
                    "category": "NETWORK_EXPOSURE",
                    "compliance_standard": "CIS_AWS_BENCHMARK_3.1",
                    "remediation_guidance": "Disable PubliclyAccessible attribute and migrate into private DB VPC subnets."
                })

        # 4. IAM Excessive Permissions
        if asset.asset_type in ["IAM_ROLE", "IAM_USER"]:
            if cfg.get("has_admin") is True or "s3:*" in cfg.get("wildcard_actions", []):
                findings.append({
                    "rule_id": "CSPM-IAM-001",
                    "title": "Over-Privileged Wildcard Permissions Attached",
                    "description": f"Identity {asset.resource_name} has broad wildcard actions violating least-privilege principles.",
                    "severity": "HIGH",
                    "category": "IAM_PRIVILEGE",
                    "compliance_standard": "CIS_AWS_BENCHMARK_1.16",
                    "remediation_guidance": "Replace wildcard * actions with scoped resource-specific IAM policies."
                })

        # 5. Kubernetes Workload Security
        if asset.asset_type in ["K8S_POD", "K8S_DEPLOYMENT"]:
            if cfg.get("privileged") is True or cfg.get("hostNetwork") is True:
                findings.append({
                    "rule_id": "CSPM-K8S-001",
                    "title": "Privileged Container Execution",
                    "description": f"Pod {asset.resource_name} runs with elevated host privileges or hostNetwork sharing.",
                    "severity": "CRITICAL",
                    "category": "KUBERNETES_WORKLOAD",
                    "compliance_standard": "CIS_K8S_BENCHMARK_5.2",
                    "remediation_guidance": "Set securityContext.privileged=false and drop all CAP_SYS_ADMIN capabilities."
                })

        return findings

    @classmethod
    async def run_full_cspm_scan(cls, db: AsyncSession, tenant_id: str) -> Dict[str, Any]:
        """Runs full CSPM compliance scan across all inventoried assets."""
        # Ensure default assets seeded if empty
        await CloudAssetInventoryService.list_assets(db, tenant_id)

        stmt = select(CloudAsset).where(CloudAsset.tenant_id == tenant_id)
        assets = list((await db.execute(stmt)).scalars().all())

        new_findings_count = 0
        for a in assets:
            detected = await cls.evaluate_asset_security_posture(a)
            for f in detected:
                # Check if existing open finding exists
                stmt_f = select(CSPMFinding).where(
                    CSPMFinding.tenant_id == tenant_id,
                    CSPMFinding.asset_id == a.id,
                    CSPMFinding.rule_id == f["rule_id"],
                    CSPMFinding.status == "OPEN"
                )
                existing = (await db.execute(stmt_f)).scalar_one_or_none()
                if not existing:
                    inst = CSPMFinding(
                        tenant_id=tenant_id,
                        asset_id=a.id,
                        rule_id=f["rule_id"],
                        title=f["title"],
                        description=f["description"],
                        severity=f["severity"],
                        category=f["category"],
                        compliance_standard=f["compliance_standard"],
                        remediation_guidance=f["remediation_guidance"],
                        status="OPEN",
                        detected_at=datetime.now(timezone.utc)
                    )
                    db.add(inst)
                    new_findings_count += 1

        await db.flush()

        # Fetch current findings summary
        all_findings = await cls.list_findings(db, tenant_id)
        critical_count = sum(1 for f in all_findings if f["severity"] == "CRITICAL")
        high_count = sum(1 for f in all_findings if f["severity"] == "HIGH")

        return {
            "total_assets_scanned": len(assets),
            "new_findings_detected": new_findings_count,
            "total_open_findings": len(all_findings),
            "critical_findings": critical_count,
            "high_findings": high_count,
            "compliance_score": max(10, 100 - (critical_count * 15 + high_count * 5)),
            "scanned_at": datetime.now(timezone.utc).isoformat()
        }

    @classmethod
    async def list_findings(cls, db: AsyncSession, tenant_id: str) -> List[Dict[str, Any]]:
        """Lists active CSPM findings."""
        stmt = select(CSPMFinding).where(CSPMFinding.tenant_id == tenant_id, CSPMFinding.status == "OPEN").order_by(desc(CSPMFinding.detected_at))
        findings = list((await db.execute(stmt)).scalars().all())

        return [
            {
                "id": f.id,
                "asset_id": f.asset_id,
                "rule_id": f.rule_id,
                "title": f.title,
                "description": f.description,
                "severity": f.severity,
                "category": f.category,
                "compliance_standard": f.compliance_standard,
                "remediation_guidance": f.remediation_guidance,
                "status": f.status,
                "detected_at": f.detected_at.isoformat() if f.detected_at else None
            }
            for f in findings
        ]
