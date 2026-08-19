"""
scripts/validate_k8s_hpa.py
===========================
Validates Horizontal Pod Autoscaler (HPA) objects and metrics-server in Kubernetes.
Verifies metrics availability, current vs target replicas, and scaling constraints.
Returns exit code 0 (PASS), 1 (FAIL), or 2 (BLOCKED).
"""

import sys
import shutil
import json
import subprocess
import argparse


def validate_hpa(namespace: str) -> int:
    print("=================================================================")
    print("      SentinelAI Kubernetes HPA & Metrics-Server Validator       ")
    print(f"Target Namespace : {namespace}")
    print("=================================================================")

    kubectl = shutil.which("kubectl")
    if not kubectl:
        print("[BLOCKED] kubectl CLI is not installed -- live HPA validation blocked.")
        return 2

    # 1. Check if metrics-server APIService or pods exist
    ms_check = subprocess.run([kubectl, "get", "apiservices", "v1beta1.metrics.k8s.io", "-o", "json"], capture_output=True, text=True)
    if ms_check.returncode != 0:
        print("[BLOCKED] metrics-server is unavailable in cluster -- HPA live metric autoscaling cannot be evaluated.")
        print("         To enable: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml")
        return 2

    # 2. Query HPAs in namespace
    hpa_res = subprocess.run([kubectl, "get", "hpa", "-n", namespace, "-o", "json"], capture_output=True, text=True)
    if hpa_res.returncode != 0:
        print(f"[FAIL] Unable to query HPA in namespace '{namespace}': {hpa_res.stderr.strip()}")
        return 1

    try:
        data = json.loads(hpa_res.stdout)
        items = data.get("items", [])
        if not items:
            print(f"[BLOCKED] Zero HPA objects found in namespace '{namespace}'.")
            return 2

        print(f"Discovered {len(items)} HPA resource(s):")
        all_ok = True
        for h in items:
            h_name = h["metadata"]["name"]
            spec = h.get("spec", {})
            status = h.get("status", {})

            min_rep = spec.get("minReplicas", 1)
            max_rep = spec.get("maxReplicas", 1)
            cur_rep = status.get("currentReplicas", 0)
            des_rep = status.get("desiredReplicas", 0)

            print(f"  - HPA: {h_name:<25} | Min: {min_rep} | Max: {max_rep} | Current: {cur_rep} | Desired: {des_rep}")
            if cur_rep < min_rep or cur_rep > max_rep:
                print(f"    [WARN] Current replicas ({cur_rep}) out of bounds [{min_rep}, {max_rep}]")
                all_ok = False

        if all_ok:
            print("\nRESULT: HPA AND METRICS-SERVER VALIDATED (PASS)")
            return 0
        else:
            print("\nRESULT: HPA METRICS INCOMPLETE (FAIL)")
            return 1

    except Exception as exc:
        print(f"[FAIL] Error parsing HPA JSON: {exc}")
        return 1


def main():
    parser = argparse.ArgumentParser(description="SentinelAI HPA Validator")
    parser.add_argument("--namespace", default="sentinelai", help="Kubernetes namespace")
    args = parser.parse_args()

    exit_code = validate_hpa(args.namespace)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
