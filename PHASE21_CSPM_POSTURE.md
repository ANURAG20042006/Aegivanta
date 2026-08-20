# AEGIVANTA — PHASE 21 CLOUD SECURITY POSTURE MANAGEMENT (CSPM)

## 1. Compliance Rule Catalog
1. `CSPM-S3-001`: Publicly accessible cloud storage bucket (CIS AWS 2.1).
2. `CSPM-S3-002`: Missing default server-side KMS/AES encryption (CIS AWS 2.2).
3. `CSPM-NET-001`: Management ports (SSH 22 / RDP 3389) open to `0.0.0.0/0` (CIS AWS 4.1).
4. `CSPM-DB-001`: Cloud database configured with public IP accessibility (CIS AWS 3.1).
5. `CSPM-IAM-001`: Over-privileged wildcard policies attached to roles/users (CIS AWS 1.16).
6. `CSPM-K8S-001`: Privileged container running with elevated host permissions (CIS K8s 5.2).

## 2. CIS Posture Scoring
Calculates composite posture score ($0–100\%$) weighted by critical and high severity misconfiguration counts.
