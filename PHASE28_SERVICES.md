# PHASE 28 — ENTERPRISE IAM & ZERO TRUST SERVICES

## 1. Services Overview

| Service Name | Path | Purpose |
|--------------|------|---------|
| `PAMService` | `backend/app/services/pam_service.py` | Just-in-Time privilege elevation workflows, approvals, and emergency revocations. |
| `ITDRService` | `backend/app/services/itdr_service.py` | Real-time identity threat detection, MITRE ATT&CK mapping, and threat simulations. |
| `ZeroTrustContinuousAuthService` | `backend/app/services/zero_trust_continuous_auth_service.py` | Continuous adaptive session authorization and dynamic verdict engine. |
| `IdentityGovernanceService` | `backend/app/services/identity_governance_service.py` | Identity risk scorecards, FIDO2 passkeys, and dormant account reaper. |
