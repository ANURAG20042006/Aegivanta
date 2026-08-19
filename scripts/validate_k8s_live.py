"""
scripts/validate_k8s_live.py
============================
Cross-platform live Kubernetes validator. Checks kubectl availability,
cluster reachability, and runs server-side dry-run validation without deployment.
"""

import sys
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
K8S_DIR = PROJECT_ROOT / "k8s"


def run_live_validation():
    print("=================================================================")
    print("      SentinelAI Live Kubernetes Server-Side Validation          ")
    print("=================================================================")

    # 1. Check kubectl availability
    kubectl_path = shutil.which("kubectl")
    if not kubectl_path:
        print("STATUS : BLOCKED")
        print("REASON : kubectl unavailable -- live Kubernetes schema validation not performed.")
        print("=================================================================")
        return 2

    # 2. Check cluster reachability
    print(f"Detected kubectl at: {kubectl_path}")
    cluster_info = subprocess.run([kubectl_path, "cluster-info"], capture_output=True, text=True)
    if cluster_info.returncode != 0:
        print("STATUS : BLOCKED")
        print("REASON : Kubernetes cluster unreachable or no active kubeconfig context.")
        print(f"DETAILS: {cluster_info.stderr.strip()}")
        print("=================================================================")
        return 2

    # 3. Execute server-side dry-run validation
    print("Executing server-side dry-run validation against active Kubernetes API server...")
    res = subprocess.run([kubectl_path, "apply", "--dry-run=server", "-f", str(K8S_DIR)], capture_output=True, text=True)

    if res.returncode == 0:
        print("STATUS : PASS")
        print(res.stdout)
        print("=================================================================")
        print("RESULT: LIVE KUBERNETES SERVER-SIDE VALIDATION PASSED")
        print("=================================================================")
        return 0
    else:
        print("STATUS : FAIL")
        print(res.stderr)
        print("=================================================================")
        print("RESULT: LIVE KUBERNETES SERVER-SIDE VALIDATION FAILED")
        print("=================================================================")
        return 1


if __name__ == "__main__":
    code = run_live_validation()
    sys.exit(code)
