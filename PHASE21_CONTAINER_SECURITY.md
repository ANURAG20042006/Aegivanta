# AEGIVANTA — PHASE 21 CONTAINER SECURITY & SBOM

## 1. Vulnerability & CVE Scanning
- Evaluates base OS and application packages against National Vulnerability Database (NVD).
- Identifies critical CVEs (e.g. `CVE-2024-21626` runc container escape, `CVE-2023-44487` HTTP/2 Rapid Reset).

## 2. Software Bill of Materials (SBOM)
- Generates standard CycloneDX 1.5 JSON manifests cataloging runtime packages, licenses, and library versions.

## 3. Cryptographic Signature Verification
- Validates Cosign / Notary v2 signatures on container digests before deployment into production clusters.
