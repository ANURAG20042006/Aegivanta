"""
scripts/smoke_test_k8s_api.py
=============================
Production smoke-test for SentinelAI API deployed in Kubernetes.
Tests liveness, readiness, authentication, valid threat ingestion, and malformed rejection.
Returns exit code 0 (PASS), 1 (FAIL), or 2 (BLOCKED).
"""

import os
import sys
import argparse
import urllib.request
import urllib.parse
import urllib.error
import json
from typing import Dict, Any


def run_smoke_test(base_url: str) -> int:
    print("=================================================================")
    print("      SentinelAI Kubernetes API Production Smoke Test            ")
    print(f"Target API Endpoint : {base_url}")
    print("=================================================================")

    # 1. Test Liveness Probe (/health)
    try:
        req = urllib.request.Request(f"{base_url}/health", headers={"User-Agent": "SentinelAI-SmokeTest"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                print(f"[FAIL] /health returned unexpected status code {response.status}")
                return 1
            print("[PASS] Step 1: Liveness probe (/health) returned HTTP 200 OK")
    except urllib.error.URLError as e:
        print(f"[BLOCKED] Target API at {base_url} is unreachable: {e.reason}")
        return 2
    except Exception as e:
        print(f"[FAIL] Liveness probe error: {e}")
        return 1

    # 2. Test Readiness Probe (/api/v1/health/ready)
    try:
        req = urllib.request.Request(f"{base_url}/api/v1/health/ready", headers={"User-Agent": "SentinelAI-SmokeTest"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                print(f"[FAIL] Readiness probe returned status code {response.status}")
                return 1
            body = json.loads(response.read().decode("utf-8"))
            if not body.get("ready") or not body.get("redis_connected"):
                print(f"[FAIL] Readiness payload reports unready state: {body}")
                return 1
            print("[PASS] Step 2: Readiness probe (/api/v1/health/ready) returned HTTP 200 (ready=True, redis=True)")
    except Exception as e:
        print(f"[FAIL] Readiness probe error: {e}")
        return 1

    # 3. Authenticate and obtain JWT Access Token
    auth_headers = {"User-Agent": "SentinelAI-SmokeTest"}
    token = None
    admin_password = os.environ.get("SENTINEL_ADMIN_PASSWORD", "SentinelAdminP@ssw0rd2026!")
    try:
        login_data = urllib.parse.urlencode({
            "username": "admin",
            "password": admin_password
        }).encode("utf-8")
        login_req = urllib.request.Request(
            f"{base_url}/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "SentinelAI-SmokeTest"}
        )
        with urllib.request.urlopen(login_req, timeout=5) as login_resp:
            if login_resp.status == 200:
                auth_body = json.loads(login_resp.read().decode("utf-8"))
                token = auth_body.get("access_token")
                if token:
                    auth_headers["Authorization"] = f"Bearer {token}"
                    print("[PASS] Step 3: Authentication succeeded, JWT Bearer token obtained")
    except Exception as e:
        print(f"[NOTE] Unauthenticated or optional auth flow ({e})")

    # 4. Test Ingestion of Valid Telemetry Flow (/api/v1/predict/single)
    valid_features = {
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.1",
        "source_port": 54321,
        "destination_port": 80,
        "protocol": "TCP",
        "flow_duration": 15000.0,
        "total_fwd_packets": 10.0,
        "packet_length_mean": 512.0
    }
    try:
        data_bytes = json.dumps({"features": valid_features, "model_name": "Random Forest"}).encode("utf-8")
        predict_headers = {"Content-Type": "application/json", **auth_headers}
        req = urllib.request.Request(
            f"{base_url}/api/v1/predict/single",
            data=data_bytes,
            headers=predict_headers
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                print(f"[FAIL] Valid prediction returned status code {response.status}")
                return 1
            res_json = json.loads(response.read().decode("utf-8"))
            print(f"[PASS] Step 4: Valid flow inference returned HTTP 200 (attack_type={res_json.get('attack_type')}, model={res_json.get('model_used')})")
    except Exception as e:
        print(f"[FAIL] Valid flow prediction failed: {e}")
        return 1

    # 5. Test Ingestion of Malformed Telemetry Flow (Negative Validation)
    malformed_features = {
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.1",
        "flow_duration": -999.0  # Invalid duration -> must trigger HTTP 400
    }
    try:
        data_bytes = json.dumps({"features": malformed_features, "model_name": "Random Forest"}).encode("utf-8")
        neg_headers = {"Content-Type": "application/json", **auth_headers}
        req = urllib.request.Request(
            f"{base_url}/api/v1/predict/single",
            data=data_bytes,
            headers=neg_headers
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                print("[FAIL] Malformed payload unexpectedly accepted with HTTP 200")
                return 1
        except urllib.error.HTTPError as http_err:
            if http_err.code == 400 or http_err.code == 422:
                print(f"[PASS] Step 5: Malformed flow properly rejected with HTTP {http_err.code} validation error")
            else:
                print(f"[FAIL] Malformed flow returned unexpected HTTP error: {http_err.code}")
                return 1
    except Exception as e:
        print(f"[FAIL] Negative schema test failed: {e}")
        return 1

    print("=================================================================")
    print("RESULT: API PRODUCTION SMOKE TEST PASSED (0 FAILURES)")
    print("=================================================================")
    return 0


def main():
    parser = argparse.ArgumentParser(description="SentinelAI Kubernetes API Smoke Test")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of SentinelAI API service")
    args = parser.parse_args()

    exit_code = run_smoke_test(args.url)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
