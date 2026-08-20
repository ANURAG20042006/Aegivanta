# Aegivanta Phase 5 — Centralized Security Policy Engine

## 1. Policy Dimensions & Guardrails

The enterprise Security Policy engine enforces fail-closed restrictions across:
- `require_mfa` (Boolean): Blocks any non-MFA login attempt when active.
- `require_sso` (Boolean): Enforces enterprise Identity Provider authentication.
- `session_timeout_minutes` (Integer): Invalidation window for idle or unrefreshed sessions.
- `max_concurrent_sessions` (Integer): Maximum active concurrent device sessions per user.
- `ip_allowlist` (JSON Array): CIDR-scoped IP whitelisting for organization access.
- `ip_denylist` (JSON Array): CIDR-scoped IP blocking.
- `api_key_max_ttl_days` (Integer): Maximum allowable lifetime for generated API keys.
