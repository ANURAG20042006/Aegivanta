# PHASE 38 — FRONTEND COMPLIANCE & DETECTION COMMAND CENTER

## 1. UI Tabs

`ComplianceDetectionCenter.tsx` delivers 6 interactive enterprise tabs:
1. **Compliance & Detection Overview**: Scorecard metrics, active rules, evaluated controls across 5 standards, audit reports count, and compliance drift tracker.
2. **Detection-as-Code (Sigma)**: Catalog of autonomous rules with lifecycle badges, MITRE mappings, TPR rates, and noise scores.
3. **Rule Sandbox Tester**: Live safe evaluation form to test candidate rules against simulated telemetry payloads with latency measurement.
4. **Regulatory Matrix (5 Standards)**: Multi-standard controls viewer with framework filtering (SOC 2, ISO 27001, HIPAA, FedRAMP, PCI-DSS) and automated evidence details.
5. **Attestation Reports**: Exportable compliance packages with cryptographic SHA-256 hashes and passing/failing control counts.
6. **Rule Compiler Studio**: Interactive editor to author, compile, and ingest candidate Sigma/YARA-L rules.
