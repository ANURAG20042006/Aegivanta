# PHASE 31 — DANGLING DNS & SUBDOMAIN TAKEOVER SPECIFICATION

## 1. Vulnerability Mechanics

1. Organization points subdomain `docs-staging.example.com` via CNAME to `example-docs.s3-website-us-east-1.amazonaws.com`.
2. S3 bucket is deleted without updating DNS.
3. Attacker creates S3 bucket with matching name and serves arbitrary malicious payloads under `docs-staging.example.com`.
4. **Aegivanta Defense**: Proactively flags orphaned CNAMEs with reachability checks and alerts with `takeover_risk_score >= 90.0`.
