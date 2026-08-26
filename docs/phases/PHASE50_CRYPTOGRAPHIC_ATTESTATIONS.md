# Phase 50: Cryptographic HSM Attestations & Binary Integrity

## Attestation Architecture
1. **Hardware Security Module (HSM) Root of Trust**: Attestation serials are digitally signed with an immutable KMS HSM master key (`kms/aegivanta-root-hsm-2026`).
2. **SHA-256 Platform Build Signatures**: Every release candidate image produces a verifiable cryptographic hash validating that zero unauthorized modifications exist.
3. **Public Key Verification**: Auditors can cryptographically verify the signature against the public HSM certificate.
