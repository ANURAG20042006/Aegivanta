# PHASE 43 — FRONTEND DATA GOVERNANCE & DSAR COMMAND CENTER

## 1. UI Tabs

`DataGovernanceCenter.tsx` delivers 6 interactive enterprise tabs:
1. **Governance Overview**: Scorecard metrics, active lineage stages, total governed records count, active legal holds, and completed DSARs.
2. **Telemetry Provenance DAG**: Multi-stage data asset graph with pipeline stages, SHA-256 transform hashes, and record counts.
3. **Forensic Legal Holds Vault**: Active litigation hold cards with matter reference, custodian, scope filters, and frozen evidence counts.
4. **GDPR / CCPA DSAR Requests**: Table of privacy access and right-to-be-forgotten requests with status, record count, and completion certificates.
5. **Cryptographic Erasure Certificates**: Diagnostic display for WORM retention policies and NIST 800-88 erasure proofs.
6. **Legal Hold & DSAR Studio**: Dual form interface to issue new legal holds or submit DSAR privacy discovery requests.
