# PHASE 28 — ENTERPRISE IAM & PAM API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/iam/summary` | Consolidated Identity Posture & Zero Trust Scorecard. |
| `GET` | `/api/v1/iam/pam/elevations` | List JIT privilege elevation requests & active sessions. |
| `POST` | `/api/v1/iam/pam/request-elevation` | Submit a time-bounded JIT privilege elevation request. |
| `POST` | `/api/v1/iam/pam/approve/{id}` | Approve and activate a JIT elevation session. |
| `POST` | `/api/v1/iam/pam/revoke/{id}` | Terminate and revoke an active JIT elevation session. |
| `GET` | `/api/v1/iam/itdr/detections` | Active ITDR identity threat alerts (MFA fatigue, spray). |
| `POST` | `/api/v1/iam/itdr/simulate-attack` | Simulate an identity threat attack for verification. |
| `POST` | `/api/v1/iam/zero-trust/evaluate-session` | Evaluate continuous session risk and issue dynamic verdict. |
| `GET` | `/api/v1/iam/passkeys` | List registered FIDO2 / WebAuthn hardware passkeys. |
| `GET` | `/api/v1/iam/governance/scorecards` | List identity posture scorecards and privilege creep index. |
| `POST` | `/api/v1/iam/governance/reap-dormant` | Flag and reap dormant accounts idle > threshold days. |
