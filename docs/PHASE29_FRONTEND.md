# PHASE 29 — FRONTEND SUPPLY CHAIN SECURITY CENTER

## 1. Tab Overview

`SupplyChainSecurityCenter.tsx` provides 6 unified tabs:
1. **Overview**: Supply Chain Scorecard, SLSA Level 3 status, package counts, priority actions.
2. **SBOM 2.0 Catalog**: Dependency inventory with direct/transitive filters and CycloneDX/SPDX export buttons.
3. **OpenVEX Exploitability**: Ledger of VEX statements with status badges and publish statement modal.
4. **SLSA Level 3 Provenance**: Attestation table with Cosign verification badges and commit SHAs.
5. **CI/CD Gatekeeper Policies**: Gating simulator evaluating release eligibility against configurable policy gates.
6. **Secret Scanner & Licenses**: Interactive code scanner testing high-entropy tokens and secrets.
