# PHASE 35 — DATA SECURITY POSTURE MANAGEMENT (DSPM) SPECIFICATION

## 1. Shadow Data Store Discovery

- Discovers and categorizes cloud datastores across AWS S3, Azure Blob, Google Cloud Storage, and RDS PostgreSQL.
- Evaluates encryption status (e.g. `UNENCRYPTED_PUBLIC`, `SSE_KMS`, `CLIENT_ENCRYPTED`).
- Assigns deterministic risk severity based on data classification tier and public access controls.
