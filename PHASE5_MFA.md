# Aegivanta Phase 5 — Multi-Factor Authentication (MFA)

## 1. RFC 6238 TOTP Engine

- **Secret Generation**: 160-bit cryptographically secure Base32 encoded secrets.
- **URI Generation**: Standard `otpauth://totp/Aegivanta:...` URIs compatible with Google Authenticator, Authy, and hardware tokens.
- **Clock Drift Tolerance**: Validates current 30-second window plus +/- 1 step offset to accommodate minor clock drift.

## 2. Emergency Recovery Codes
Users receive 8 single-use emergency recovery codes (`XXXX-XXXX`). Hashes are stored via SHA-256; once a recovery code is used for authentication, it is permanently consumed and removed from the active set.
