# Aegivanta — Continuous Security Validation Framework (Phase 26.1)

## Overview

The Continuous Security Validation Engine continuously and empirically verifies 16 distinct security control domains across authentication, authorization, tenant isolation, cryptographic integrity, and adversarial defenses.

## 16 Verified Security Control Domains

| # | Domain Category | Control Name | Severity | Remediation |
|:---:|---|---|:---:|---|
| 1 | `AUTH` | JWT Token & Password Hashing Policy | CRITICAL | Rotate runtime secret key, enforce bcrypt work factor >= 12 |
| 2 | `RBAC` | Role-Based Access Control Boundaries | HIGH | Audit role-to-permission mapping and revoke elevated roles |
| 3 | `TENANT_ISOLATION` | Multi-Tenant SQL Boundary Enforcement | CRITICAL | Enforce tenant_id filtering and verify resolve_tenant_context |
| 4 | `API_KEYS` | Customer API Key Cryptographic Storage | HIGH | Revoke plaintext keys, enforce SHA-256 storage |
| 5 | `SENSORS` | Sensor Mutual Token Authentication | HIGH | Trigger automated 90-day token rotation |
| 6 | `WEBHOOKS` | Outbound Webhook Signing & Anti-Replay | HIGH | Configure signing secrets and enforce replay nonces |
| 7 | `SSO` | Enterprise SSO CSRF Nonce State | MEDIUM | Ensure anti-CSRF state parameter validation in IdP |
| 8 | `SCIM` | SCIM 2.0 Bearer Token Scoping | MEDIUM | Rotate SCIM provisioning credentials |
| 9 | `ENDPOINT_XDR` | Containment Action Policy Gating | CRITICAL | Enable mandatory human approval for destructive actions |
| 10 | `ZERO_TRUST` | Device Trust Score Calibration | HIGH | Calibrate zero_trust_engine factor weighting |
| 11 | `AUDIT_INTEGRITY` | Immutable Audit Hash-Chain Continuity | CRITICAL | Execute audit repair and review unauthorized DB writes |
| 12 | `ENCRYPTION` | Transport & Rest Encryption (TLS 1.3 / AES) | HIGH | Upgrade TLS certificates, verify disk encryption |
| 13 | `SECRET_REDACTION` | Telemetry & Log Token Masking | MEDIUM | Update regex filters to redact token formats |
| 14 | `RATE_LIMITING` | Sliding-Window Quota Verification | MEDIUM | Tune rate limiting sliding window burst capacity |
| 15 | `SECURITY_HEADERS` | HTTP Security Headers Configuration | LOW | Inject HSTS, CSP, X-Frame-Options headers |
| 16 | `AI_DEFENSES` | AI Prompt Injection & Extraction Defense | HIGH | Update adversarial defense heuristics in AI engine |

## API Endpoints

- `GET /api/v1/security/continuous-validation`: Retrieve latest validation summary
- `POST /api/v1/security/continuous-validation/run`: Execute on-demand validation
- `GET /api/v1/security/continuous-validation/history`: Retrieve historical runs
