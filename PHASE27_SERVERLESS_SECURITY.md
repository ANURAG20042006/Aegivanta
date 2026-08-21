# PHASE 27 — SERVERLESS SECURITY BEST PRACTICES

## 1. Serverless Posture Assessment

1. **IAM Scoping**: Replace `*` wildcard resource actions with explicit ARN resource definitions.
2. **Secret Management**: Never store secrets in plain environment variables; utilize AWS Secrets Manager or GCP Secret Manager.
3. **Public URL Triggers**: Enforce AWS IAM authentication on Lambda Function URLs unless intended for public webhooks.
4. **Runtime Currency**: Deprecate outdated runtimes (Node 14, Python 3.8) to maintain CVE patch coverage.
