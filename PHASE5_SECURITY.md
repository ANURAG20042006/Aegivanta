# Aegivanta Phase 5 — Security Architecture & Hardening

## 1. Enterprise Security Controls

1. **Authentication & MFA Enforcement**: Strict enforcement of TOTP or SSO with zero bypasses.
2. **Session Hijacking Defense**: IP and User-Agent fingerprinting flags suspicious sessions on location change.
3. **Fail-Closed Policy Engine**: Unmatched IP allowlists or unverified MFA logins reject connections immediately.
4. **Secret Protection**: All TOTP secrets, recovery codes, SCIM tokens, and session tokens are cryptographically hashed using SHA-256.
