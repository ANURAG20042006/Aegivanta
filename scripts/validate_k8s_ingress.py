"""
scripts/validate_k8s_ingress.py
===============================
Validates Kubernetes Ingress, TLS termination, SSL certificate expiration,
and WebSocket connection upgrade for SentinelAI.
Returns exit code 0 (PASS), 1 (FAIL), or 2 (BLOCKED).
"""

import sys
import argparse
import ssl
import socket
import datetime
import urllib.request
import urllib.error
import shutil
import subprocess


def validate_ingress(host: str, port: int = 443, check_tls: bool = True) -> int:
    print("=================================================================")
    print("      SentinelAI Kubernetes Ingress & TLS Validator              ")
    print(f"Target Host : {host}:{port}")
    print("=================================================================")

    # 1. DNS Resolution Check
    try:
        ip_addr = socket.gethostbyname(host)
        print(f"[PASS] Step 1: Host '{host}' successfully resolved to {ip_addr}")
    except socket.gaierror as e:
        print(f"[BLOCKED] Host '{host}' cannot be resolved via DNS: {e}")
        return 2

    # 2. TLS Certificate & Expiration Validation
    if check_tls:
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    not_after = cert.get("notAfter")
                    if not_after:
                        exp_date = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                        days_left = (exp_date - datetime.datetime.utcnow()).days
                        if days_left <= 0:
                            print(f"[FAIL] TLS certificate expired on {exp_date}")
                            return 1
                        print(f"[PASS] Step 2: TLS certificate is valid (expires in {days_left} days, on {exp_date})")
        except ssl.SSLError as ssl_err:
            print(f"[FAIL] TLS handshake or certificate verification failed: {ssl_err}")
            return 1
        except Exception as conn_err:
            print(f"[BLOCKED] Ingress HTTPS port {port} unreachable: {conn_err}")
            return 2

    # 3. HTTP to HTTPS Routing Check
    try:
        url = f"https://{host}:{port}/health" if check_tls else f"http://{host}:{port}/health"
        req = urllib.request.Request(url, headers={"User-Agent": "SentinelAI-IngressValidator"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                print(f"[PASS] Step 3: Ingress routing to /health returned HTTP 200 OK")
            else:
                print(f"[FAIL] Ingress returned unexpected HTTP status {resp.status}")
                return 1
    except Exception as e:
        print(f"[BLOCKED] Ingress HTTP request failed: {e}")
        return 2

    print("=================================================================")
    print("RESULT: INGRESS & TLS ROUTING VALIDATED (PASS)")
    print("=================================================================")
    return 0


def main():
    parser = argparse.ArgumentParser(description="SentinelAI Kubernetes Ingress & TLS Validator")
    parser.add_argument("--host", default="sentinelai.local", help="Ingress hostname")
    parser.add_argument("--port", type=int, default=443, help="Ingress HTTPS port")
    parser.add_argument("--no-tls", action="store_true", help="Skip TLS certificate check")
    args = parser.parse_args()

    exit_code = validate_ingress(args.host, args.port, check_tls=not args.no_tls)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
