# PHASE 33 — TRACEABLE CANARY TOKENS SPECIFICATION

## 1. Canary Token Types

- **AWS IAM API Keys**: Inactive API keys placed in `.aws/credentials` or env files. AWS CloudTrail generates immediate alerts when invoked.
- **Word / PDF Webhook Documents**: Embedded tracking beacons in fake confidential documents triggering instant HTTP webhooks upon opening.
- **DNS Canary Subdomains**: Custom subdomains resolving to Aegivanta DNS servers alerting upon DNS lookup.
- **Kubeconfig & DB Credentials**: Fake cluster access tokens or database credentials triggering auth failures in decoy targets.
