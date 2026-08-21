# PHASE 29 — SUPPLY CHAIN API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/supply-chain/summary` | Consolidated Supply Chain & SLSA Scorecard. |
| `GET` | `/api/v1/supply-chain/sbom/components` | List third-party dependency components and license flags. |
| `POST` | `/api/v1/supply-chain/sbom/generate` | Export CycloneDX 1.5 or SPDX 2.3 JSON document. |
| `GET` | `/api/v1/supply-chain/vex/statements` | List OpenVEX exploitability determinations. |
| `POST` | `/api/v1/supply-chain/vex/publish` | Publish OpenVEX statement. |
| `GET` | `/api/v1/supply-chain/vex/export` | Export compliant OpenVEX format manifest. |
| `GET` | `/api/v1/supply-chain/slsa/attestations` | List SLSA Level 3 provenance records. |
| `POST` | `/api/v1/supply-chain/slsa/verify` | Verify artifact digest and Cosign signature. |
| `GET` | `/api/v1/supply-chain/gates` | List CI/CD security gatekeeper policies. |
| `POST` | `/api/v1/supply-chain/gates/evaluate` | Evaluate pipeline build against deployment policy. |
| `POST` | `/api/v1/supply-chain/secrets/scan` | Scan code text for secrets and API tokens. |
