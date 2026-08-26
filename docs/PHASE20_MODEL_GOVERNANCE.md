# AEGIVANTA — PHASE 20 MODEL GOVERNANCE & INTEGRITY

## 1. Cryptographic HMAC-SHA256 Signing
Every model artifact registered in `AIModelGovernance` is sealed with an HMAC-SHA256 signature calculated from its raw SHA-256 payload hash and tenant/server secret.

## 2. Promotion & Rollback Lifecycle
- `STAGING`: Initial registration state for validation.
- `CANARY`: Shadow serving against a subset of production sensor telemetry.
- `PRODUCTION`: Active inference serving model version.
- `ROLLED_BACK`: Atomic 1-click rollback state demoting faulty models.
