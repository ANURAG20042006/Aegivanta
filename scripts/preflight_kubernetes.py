"""
scripts/preflight_kubernetes.py
===============================
Pre-flight Kubernetes environment and CLI connectivity validator.
Verifies kubectl installation, version compatibility, active kubeconfig context,
and Kubernetes API server reachability.
Outputs machine-readable status: PASS, BLOCKED, or FAIL.
"""

import sys
import shutil
import json
import subprocess
from typing import Dict, Any, Tuple


def check_kubernetes_preflight() -> Tuple[str, Dict[str, Any]]:
    report = {
        "kubectl_installed": False,
        "kubectl_version": None,
        "current_context": None,
        "api_server_reachable": False,
        "cluster_info": None,
        "status": "BLOCKED",
        "reason": ""
    }

    # 1. Check kubectl binary presence
    kubectl = shutil.which("kubectl")
    if not kubectl:
        report["status"] = "BLOCKED"
        report["reason"] = "kubectl CLI binary is not installed or not present in system PATH."
        return report["status"], report

    report["kubectl_installed"] = True

    # 2. Query kubectl client version
    ver_res = subprocess.run([kubectl, "version", "--client", "-o", "json"], capture_output=True, text=True)
    if ver_res.returncode == 0:
        try:
            ver_data = json.loads(ver_res.stdout)
            report["kubectl_version"] = ver_data.get("clientVersion", {}).get("gitVersion")
        except Exception:
            report["kubectl_version"] = "unknown"
    else:
        # Fallback to plain text version
        ver_res_plain = subprocess.run([kubectl, "version", "--client"], capture_output=True, text=True)
        report["kubectl_version"] = ver_res_plain.stdout.strip()

    # 3. Check current context
    ctx_res = subprocess.run([kubectl, "config", "current-context"], capture_output=True, text=True)
    if ctx_res.returncode != 0 or not ctx_res.stdout.strip():
        report["status"] = "BLOCKED"
        report["reason"] = "No active Kubernetes context found in kubeconfig (~/.kube/config)."
        return report["status"], report

    report["current_context"] = ctx_res.stdout.strip()

    # 4. Check API server connectivity and authentication
    info_res = subprocess.run([kubectl, "cluster-info"], capture_output=True, text=True)
    if info_res.returncode != 0:
        err_msg = info_res.stderr.strip().lower()
        if "unauthorized" in err_msg or "forbidden" in err_msg or "authentication" in err_msg:
            report["status"] = "FAIL"
            report["reason"] = f"Kubernetes API server authentication failed: {info_res.stderr.strip()}"
        else:
            report["status"] = "BLOCKED"
            report["reason"] = f"Kubernetes API server unreachable: {info_res.stderr.strip()}"
        return report["status"], report

    report["api_server_reachable"] = True
    report["cluster_info"] = info_res.stdout.strip().split("\n")[0]
    report["status"] = "PASS"
    report["reason"] = "Kubernetes CLI and cluster context verified successfully."
    return report["status"], report


def main():
    status, report = check_kubernetes_preflight()
    print("=================================================================")
    print("        SentinelAI Kubernetes Pre-Flight Check                   ")
    print("=================================================================")
    print(f"PREFLIGHT STATUS   : {status}")
    print(f"Kubectl Installed  : {report['kubectl_installed']}")
    print(f"Kubectl Version    : {report['kubectl_version']}")
    print(f"Active Context     : {report['current_context']}")
    print(f"API Server Reachable: {report['api_server_reachable']}")
    print(f"Details / Reason   : {report['reason']}")
    print("=================================================================")

    if status == "PASS":
        sys.exit(0)
    elif status == "BLOCKED":
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
