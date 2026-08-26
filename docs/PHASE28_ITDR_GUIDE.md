# PHASE 28 — ITDR DETECTION & TRIAGE GUIDE

## 1. Attack Signatures & Triage

1. **MFA Push Fatigue (T1621)**:
   - **Signal**: >5 push notification prompts in under 3 minutes.
   - **Automated Response**: Immediate step-up challenge requiring FIDO2 WebAuthn / Passkey biometric confirmation.
2. **Distributed Password Spraying (T1110.003)**:
   - **Signal**: Single IP attempting 1-2 passwords against dozens of accounts.
   - **Automated Response**: Rate-limit IP and trigger smart lockouts without locking user accounts globally.
