# SentinelAI Security Architecture & Standards

## 1. Authentication & JWT Security
- **Algorithm**: Standard `HS256` HMAC-SHA256 signature.
- **Signing Key**: Cryptographic `SECRET_KEY` loaded from environment variables (minimum 32 characters in production). Randomly generated per process in development (`_RUNTIME_DEV_SECRET`).
- **Token Expiration**: Configured via `ACCESS_TOKEN_EXPIRE_MINUTES` (default 480 minutes / 8 hours).
- **Password Hashing**: Native `bcrypt` salted hash (`bcrypt.hashpw`), truncated to 72 bytes per bcrypt specification. Plaintext passwords and secret tokens are never stored, logged, or returned in API responses.

---

## 2. Strict Production Secret Management
Production environment enforces mandatory environment variables:
- `SECRET_KEY`: High-entropy random secret (>= 32 characters).
- `POSTGRES_PASSWORD`: Production database user password.
- `SENTINEL_ADMIN_PASSWORD`: System administrator account password.
- `SENTINEL_ANALYST_PASSWORD`: Senior analyst account password.
- `SENTINEL_VIEWER_PASSWORD`: Viewer account password.

`validate_production_settings()` stops application startup immediately if any of these secrets are missing or if development CORS origins / debug flags are enabled in production.

---

## 3. Threat Mitigation & Defensive Practices
- **Authentication Error Generic Messages**: Auth failures return generic `"Invalid username or password."` to prevent user enumeration attacks.
- **Sanitized Audit Telemetry**: Audit logs capture actor IDs, timestamps, actions, resources, and operating modes without recording credentials or JWT headers.
- **Fail-Closed Verification**: Model rollbacks, artifact schema checks, and endpoint role requirements fail closed, returning HTTP 401 or 403 on authorization failure.
