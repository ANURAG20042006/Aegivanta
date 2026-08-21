# Aegivanta — Final Security Architecture & Control Verification (v25.0.0)

## 1. Authentication & Identity
- **Enterprise SSO**: RFC-compliant OIDC & SAML 2.0 with anti-CSRF nonce state parameters.
- **MFA Enforcement**: RFC 6238 TOTP with Base32 cryptographic secret generation and bcrypt-hashed recovery codes.
- **SCIM 2.0**: RFC 7644 user lifecycle synchronization with instant deactivation.
- **API Key Security**: High-entropy 192-bit keys stored exclusively as SHA-256 digests with sliding rate limiting.

## 2. Telemetry Ingestion & Sensor Security
- **Per-Sensor Credentials**: 90-day cryptographic rotating tokens.
- **Replay & Expansion Defense**: Sliding-window LRU deduplication, decompression safety caps (10MB).
- **Tenant Boundary Enforcement**: Strict SQL filters and schema isolation preventing cross-tenant data contamination.

## 3. Autonomous Remediation & AI Guardrails
- **Zero Unattended Destruction**: High-impact SOAR and EDR actions require explicit analyst approval.
- **SOAR Kill Switches**: Global emergency revocation for automated containment policies.
- **Adversarial Defenses**: Prompt injection filtering, model extraction throttling, data poisoning validation.
- **Integration Security**: HMAC-SHA256 signing for all outbound webhooks, nonce replay protection, encrypted secret storage.

## 4. Endpoint XDR & Cloud Posture Security
- **EDR Detection**: Behavioral process anomaly detection, ransomware shadow copy defense, credential dumping detection.
- **Zero-Trust Device Trust Engine**: Dynamic trust scoring (0–100) based on patch status, EDR health, encryption, firewall.
- **Cloud Infrastructure Posture**: CSPM, KSPM, and CIEM analyzers with automated attack path synthesis.
