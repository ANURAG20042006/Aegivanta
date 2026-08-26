# PHASE 29 — CI/CD GATEKEEPER POLICY ENGINE

## 1. Gating Thresholds

- **Production Gate**: `BLOCKING` mode. Max 0 Critical CVEs, Max 0 High CVEs, mandatory SLSA Level 3, disallow copyleft licenses, 0 secrets.
- **Staging Gate**: `AUDIT_ONLY` mode. Max 1 Critical CVE, Max 3 High CVEs.
- **Bypass Protocol**: Requires signed OpenVEX justification or explicit Break-Glass authorization.
