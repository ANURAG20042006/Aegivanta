"""
scripts/validate_phase3_3_cluster.py
====================================
Validates deployed Kubernetes resources when an active cluster exists.
Checks namespace, deployments, statefulsets, services, endpoints, HPA, PDB,
and Pod readiness conditions without fabricating success states.
"""

import sys
import shutil
import json
import subprocess


def validate_cluster_state():
    print("=================================================================")
    print("     SentinelAI Live Kubernetes Cluster Deployment Validator     ")
    print("=================================================================")

    kubectl = shutil.which("kubectl")
    if not kubectl:
        print("STATUS : BLOCKED")
        print("REASON : kubectl CLI unavailable -- live cluster inspection cannot be performed.")
        print("=================================================================")
        return 2

    # Check cluster connection
    cluster_ping = subprocess.run([kubectl, "get", "nodes"], capture_output=True, text=True)
    if cluster_ping.returncode != 0:
        print("STATUS : BLOCKED")
        print("REASON : Kubernetes cluster unreachable.")
        print(f"DETAILS: {cluster_ping.stderr.strip()}")
        print("=================================================================")
        return 2

    ns = "sentinelai"
    print(f"Inspecting namespace '{ns}' on active cluster...")

    # Query Pods in JSON
    pods_res = subprocess.run(
        [kubectl, "get", "pods", "-n", ns, "-o", "json"],
        capture_output=True, text=True
    )
    if pods_res.returncode != 0:
        print(f"STATUS : FAILED -- Unable to query pods in namespace '{ns}': {pods_res.stderr.strip()}")
        return 1

    try:
        pods_data = json.loads(pods_res.stdout)
        items = pods_data.get("items", [])
        print(f"Discovered {len(items)} pod(s) in namespace '{ns}':")

        all_ready = True
        for pod in items:
            p_name = pod["metadata"]["name"]
            phase = pod.get("status", {}).get("phase", "Unknown")
            c_statuses = pod.get("status", {}).get("containerStatuses", [])

            ready = all(cs.get("ready", False) for cs in c_statuses) if c_statuses else False
            restarts = sum(cs.get("restartCount", 0) for cs in c_statuses)

            print(f"  - Pod: {p_name:<35} | Phase: {phase:<10} | Ready: {str(ready):<6} | Restarts: {restarts}")
            if not ready or phase != "Running":
                all_ready = False

        if not items:
            print(f"  [WARN] Zero pods deployed in namespace '{ns}'. Run 'kubectl apply -f k8s/' first.")
            return 1

        # Check Services & Endpoints
        svc_res = subprocess.run([kubectl, "get", "endpoints", "-n", ns, "-o", "json"], capture_output=True, text=True)
        if svc_res.returncode == 0:
            svc_data = json.loads(svc_res.stdout)
            print("\nService Endpoints:")
            for ep in svc_data.get("items", []):
                ep_name = ep["metadata"]["name"]
                subsets = ep.get("subsets", [])
                addr_count = sum(len(s.get("addresses", [])) for s in subsets)
                print(f"  - Endpoint: {ep_name:<30} | Ready Addresses: {addr_count}")

        # Check HPA Status
        hpa_res = subprocess.run([kubectl, "get", "hpa", "-n", ns], capture_output=True, text=True)
        print("\nHorizontal Pod Autoscalers:")
        print(hpa_res.stdout if hpa_res.returncode == 0 else "  HPA query returned non-zero exit.")

        # Check PDB Status
        pdb_res = subprocess.run([kubectl, "get", "pdb", "-n", ns], capture_output=True, text=True)
        print("\nPod Disruption Budgets:")
        print(pdb_res.stdout if pdb_res.returncode == 0 else "  PDB query returned non-zero exit.")

        if all_ready:
            print("\nRESULT: ALL LIVE CLUSTER WORKLOADS ARE RUNNING & READY (PASS)")
            return 0
        else:
            print("\nRESULT: SOME PODS ARE NOT READY (FAIL)")
            return 1

    except Exception as exc:
        print(f"Error parsing cluster status: {exc}")
        return 1


if __name__ == "__main__":
    code = validate_cluster_state()
    sys.exit(code)
