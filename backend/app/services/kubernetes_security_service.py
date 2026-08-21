"""
backend/app/services/kubernetes_security_service.py
==================================================
Phase 21 & Phase 27 Kubernetes Security Posture Management (KSPM) Service.
Audits Kubernetes YAML manifests, Pod security standards, RBAC policies, and cluster postures.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.cloud_security import KubernetesCluster

logger = logging.getLogger("Aegivanta.KubernetesSecurity")


class KubernetesSecurityService:
    """Audits Kubernetes manifests, PodSecurityStandards, and RBAC policies."""

    @classmethod
    async def list_clusters(
        cls,
        db: AsyncSession,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Lists registered Kubernetes clusters with KSPM compliance posture."""
        stmt = select(KubernetesCluster).where(
            KubernetesCluster.tenant_id == tenant_id
        ).order_by(desc(KubernetesCluster.kspm_health_score))

        clusters = list((await db.execute(stmt)).scalars().all())

        if not clusters:
            # Seed default clusters
            defaults = [
                ("EKS-Production-Cluster-01", "EKS", "v1.28.4", 12, 148, True, "RESTRICTED", 0, 94.0),
                ("GKE-Data-Analytics-Prod", "GKE", "v1.29.1", 6, 64, True, "BASELINE", 1, 88.0),
                ("AKS-Staging-Cluster", "AKS", "v1.27.8", 4, 32, False, "PRIVILEGED", 3, 68.0)
            ]
            for name, dist, ver, nodes, pods, adm, pss, priv, score in defaults:
                inst = KubernetesCluster(
                    tenant_id=tenant_id,
                    cluster_name=name,
                    distribution=dist,
                    k8s_version=ver,
                    node_count=nodes,
                    pod_count=pods,
                    admission_controller_enforced=adm,
                    pod_security_standard=pss,
                    privileged_workloads_count=priv,
                    kspm_health_score=score,
                    last_audited_at=datetime.now(timezone.utc)
                )
                db.add(inst)
            await db.flush()

            stmt2 = select(KubernetesCluster).where(KubernetesCluster.tenant_id == tenant_id)
            clusters = list((await db.execute(stmt2)).scalars().all())

        return [
            {
                "id": c.id,
                "cluster_name": c.cluster_name,
                "distribution": c.distribution,
                "k8s_version": c.k8s_version,
                "node_count": c.node_count,
                "pod_count": c.pod_count,
                "admission_controller_enforced": c.admission_controller_enforced,
                "pod_security_standard": c.pod_security_standard,
                "privileged_workloads_count": c.privileged_workloads_count,
                "kspm_health_score": c.kspm_health_score,
                "last_audited_at": c.last_audited_at.isoformat()
            }
            for c in clusters
        ]

    @classmethod
    async def enroll_cluster(
        cls,
        db: AsyncSession,
        tenant_id: str,
        cluster_name: str,
        distribution: str = "EKS",
        k8s_version: str = "v1.28.4",
        node_count: int = 5,
        pod_security_standard: str = "RESTRICTED"
    ) -> KubernetesCluster:
        """Enrolls a new Kubernetes cluster into KSPM monitoring."""
        cluster = KubernetesCluster(
            tenant_id=tenant_id,
            cluster_name=cluster_name,
            distribution=distribution.upper(),
            k8s_version=k8s_version,
            node_count=node_count,
            pod_count=node_count * 8,
            admission_controller_enforced=True,
            pod_security_standard=pod_security_standard.upper(),
            privileged_workloads_count=0,
            kspm_health_score=95.0,
            last_audited_at=datetime.now(timezone.utc)
        )
        db.add(cluster)
        await db.flush()
        return cluster

    @classmethod
    def audit_manifest_content(cls, manifest_yaml: str) -> Dict[str, Any]:
        """Parses and audits a Kubernetes manifest for security misconfigurations."""
        violations = []
        is_compliant = True

        # 1. Privileged Container Flag Check
        if re.search(r"privileged:\s*true", manifest_yaml, re.IGNORECASE):
            violations.append({
                "rule": "K8S-SEC-001",
                "severity": "CRITICAL",
                "title": "Privileged Container Execution Enabled",
                "description": "Container runs with full host root access, bypassing container boundary isolation.",
                "remediation": "Set securityContext.privileged: false and drop all unnecessary Linux capabilities."
            })
            is_compliant = False

        # 2. Host Network / Host PID / Host IPC
        if re.search(r"hostNetwork:\s*true", manifest_yaml, re.IGNORECASE):
            violations.append({
                "rule": "K8S-SEC-002",
                "severity": "HIGH",
                "title": "Host Network Namespace Sharing",
                "description": "Pod shares network namespace with host node, allowing sniffing of node-level traffic.",
                "remediation": "Disable hostNetwork: false and use Kubernetes Service or Ingress routing."
            })
            is_compliant = False

        if re.search(r"hostPID:\s*true", manifest_yaml, re.IGNORECASE):
            violations.append({
                "rule": "K8S-SEC-003",
                "severity": "HIGH",
                "title": "Host PID Namespace Sharing",
                "description": "Pod can view and signal processes running outside the container on the host node.",
                "remediation": "Remove hostPID: true."
            })
            is_compliant = False

        # 3. Dangerous Linux Capabilities
        if re.search(r"CAP_SYS_ADMIN|CAP_NET_ADMIN|CAP_NET_RAW", manifest_yaml, re.IGNORECASE):
            violations.append({
                "rule": "K8S-SEC-004",
                "severity": "HIGH",
                "title": "Dangerous Linux Capabilities Added",
                "description": "Workload requests elevated Linux capabilities (CAP_SYS_ADMIN/CAP_NET_RAW).",
                "remediation": "Drop ALL capabilities and only add specific least-privilege capabilities required."
            })
            is_compliant = False

        # 4. Hardcoded Plaintext Secrets in Env
        if re.search(r"(password|api_key|secret|token):\s*['\"][^'\"]+['\"]|(name:\s*['\"]?(API_KEY|PASSWORD|SECRET|TOKEN)['\"]?\s*\n\s*value:\s*['\"][^'\"]+['\"])", manifest_yaml, re.IGNORECASE):
            violations.append({
                "rule": "K8S-SEC-005",
                "severity": "CRITICAL",
                "title": "Hardcoded Plaintext Credentials in Manifest",
                "description": "Sensitive credentials found in plain environment variables rather than secretKeyRef.",
                "remediation": "Use Kubernetes Secrets with valueFrom.secretKeyRef."
            })
            is_compliant = False

        # 5. Missing Read-Only Root Filesystem
        if "readOnlyRootFilesystem: true" not in manifest_yaml:
            violations.append({
                "rule": "K8S-SEC-006",
                "severity": "MEDIUM",
                "title": "Mutable Root Filesystem",
                "description": "Container root filesystem is writable, allowing attackers to write persistent payloads.",
                "remediation": "Set securityContext.readOnlyRootFilesystem: true and mount emptyDir volumes for temporary writes."
            })

        # Calculate Posture Score
        crit_count = sum(1 for v in violations if v["severity"] == "CRITICAL")
        high_count = sum(1 for v in violations if v["severity"] == "HIGH")
        score = max(0, 100 - (crit_count * 25 + high_count * 15 + len(violations) * 5))

        return {
            "is_compliant": is_compliant,
            "workload_security_score": score,
            "violations_count": len(violations),
            "critical_violations": crit_count,
            "high_violations": high_count,
            "violations": violations,
            "audit_timestamp": datetime.now(timezone.utc).isoformat()
        }
