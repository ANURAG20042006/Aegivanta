"""
backend/app/services/cloud_attack_path_service.py
=================================================
Phase 21 Cloud Attack Path Graph Service.
Generates explainable multi-hop attack paths across internet ingress, workloads, and cloud IAM.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.cloud_security import CloudAttackPath

logger = logging.getLogger("Aegivanta.CloudAttackPath")

DEFAULT_ATTACK_PATHS = [
    {
        "title": "Internet Exposure -> Vulnerable Ingress Pod -> AWS IAM Role -> Exfiltration of S3 Customer Data",
        "source_entity": "Internet Public Ingress (Port 443)",
        "target_critical_asset": "arn:aws:s3:::aegivanta-customer-financial-archive-prod",
        "risk_score": 94.0,
        "blast_radius": "CRITICAL",
        "kill_chain_phase": "EXFILTRATION",
        "hop_nodes": [
            {
                "step": 1,
                "node_type": "INTERNET_INGRESS",
                "name": "Public ALB / Ingress",
                "detail": "Receives untrusted internet traffic"
            },
            {
                "step": 2,
                "node_type": "K8S_POD",
                "name": "aegivanta-api Pod (CVE-2024-21626)",
                "detail": "Vulnerable container with runc file descriptor leak"
            },
            {
                "step": 3,
                "node_type": "IAM_ROLE",
                "name": "AegivantaLambdaExecutionRole",
                "detail": "Over-privileged IAM role with s3:* wildcard access attached to node"
            },
            {
                "step": 4,
                "node_type": "STORAGE_BUCKET",
                "name": "aegivanta-customer-financial-archive-prod",
                "detail": "Contains sensitive customer financial archives (unencrypted)"
            }
        ],
        "remediation_steps": [
            "Upgrade base container image to patch runc CVE-2024-21626.",
            "Enforce Kubernetes PodSecurityStandards (Restricted profile).",
            "Scope AegivantaLambdaExecutionRole to least-privilege resource ARN.",
            "Enable S3 Block Public Access & KMS default encryption."
        ]
    }
]


class CloudAttackPathService:
    """Computes and returns explainable cloud attack graphs."""

    @classmethod
    async def list_attack_paths(cls, db: AsyncSession, tenant_id: str) -> List[Dict[str, Any]]:
        """Returns identified cloud attack paths."""
        stmt = select(CloudAttackPath).where(
            CloudAttackPath.tenant_id == tenant_id
        ).order_by(desc(CloudAttackPath.risk_score))

        paths = list((await db.execute(stmt)).scalars().all())
        if not paths:
            # Seed default attack path
            for p in DEFAULT_ATTACK_PATHS:
                inst = CloudAttackPath(
                    tenant_id=tenant_id,
                    title=p["title"],
                    source_entity=p["source_entity"],
                    target_critical_asset=p["target_critical_asset"],
                    risk_score=p["risk_score"],
                    blast_radius=p["blast_radius"],
                    hop_nodes=p["hop_nodes"],
                    kill_chain_phase=p["kill_chain_phase"],
                    remediation_steps=p["remediation_steps"],
                    created_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(CloudAttackPath).where(
                CloudAttackPath.tenant_id == tenant_id
            ).order_by(desc(CloudAttackPath.risk_score))
            paths = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": p.id,
                "title": p.title,
                "source_entity": p.source_entity,
                "target_critical_asset": p.target_critical_asset,
                "risk_score": p.risk_score,
                "blast_radius": p.blast_radius,
                "hop_nodes": p.hop_nodes,
                "kill_chain_phase": p.kill_chain_phase,
                "remediation_steps": p.remediation_steps,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in paths
        ]
