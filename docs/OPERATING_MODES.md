# SentinelAI Operating Modes & Safety Framework

## 1. Operating Modes

SentinelAI operates under three strict, server-side validated modes configured via `OPERATING_MODE` in environment variables:

1. **DEMO**
   - Intended for demonstration, sandboxed UI exploration, and offline evaluation.
   - Synthetic traffic flow data and simulated incidents are explicitly tagged (`is_demo: true`, `mode: "SIMULATION MODE"`).
   - Threat remediation actions execute in **SIMULATION MODE** (no active network perimeter rule changes).

2. **LAB**
   - Intended for controlled lab testing, staging integration, and sandbox network evaluation.
   - Remediation actions execute under **REAL LAB MODE** (controlled lab network isolation triggers).

3. **PRODUCTION**
   - Real enterprise deployment mode.
   - Strict security configuration validation enforced at startup (`validate_production_settings()`).
   - Requires explicit non-default credentials (`SECRET_KEY`, `POSTGRES_PASSWORD`, `SENTINEL_*_PASSWORD`).
   - Remediation actions execute under **PRODUCTION MODE** requiring explicit analyst authorization and generate audit logs.

---

## 2. Server-Side Operating Mode Validation

Application startup validates `OPERATING_MODE` against allowed options `["DEMO", "LAB", "PRODUCTION"]`. Invalid operating modes immediately halt startup with an explicit `RuntimeError`.
