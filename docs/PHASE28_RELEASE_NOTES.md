# PHASE 28 — RELEASE NOTES (v28.0.0)

## 1. Release Highlights

- **Privileged Access Management (PAM)**: Just-in-Time (JIT) privilege elevation requests, mandatory approvals, time-bounded expiration, and session audit logs.
- **Identity Threat Detection & Response (ITDR)**: Real-time detection of MFA push fatigue, password spraying, impossible travel, and Kerberoasting.
- **Continuous Zero Trust Adaptive Authorization**: Dynamic session access evaluation issuing `ALLOW`, `STEP_UP_MFA`, `RESTRICTED_MODE`, and `TERMINATE_SESSION` verdicts.
- **FIDO2 / WebAuthn Passkeys**: Full lifecycle management for hardware security keys and biometric authenticators.
- **Identity Governance & Dormant Reaper**: Automated dormancy identification (>90 days) and per-user identity risk scorecards.
- **6-Tab Frontend Command Center**: Implemented `EnterpriseIAMCenter.tsx` in React 18, TypeScript, and TailwindCSS.
- **Zero-Failure Verification**: 100% test pass rate across 10 test suites and clean Vite production build.
