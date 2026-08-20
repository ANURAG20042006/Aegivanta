"""
backend/app/services/kubernetes_security_service.py
==================================================
Phase 21 Kubernetes Security Posture Management (KSPM) Service.
Audits Kubernetes YAML manifests, Pod security contexts, and RBAC configs.
"""

import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger("Aegivanta.KubernetesSecurity")


class KubernetesSecurityService:
    """Audits Kubernetes manifests, PodSecurityStandards, and RBAC policies."""

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
            "audit_timestamp": "now"
        }
