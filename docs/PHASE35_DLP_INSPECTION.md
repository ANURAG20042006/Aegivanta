# PHASE 35 — DLP INSPECTION ENGINE SPECIFICATION

## 1. Supported Data Classifications

- **PCI-DSS Credit Card PANs**: 13 to 19 digit strings verified via Luhn mod-10 formula.
- **US Social Security Numbers (SSN)**: Regex `\b\d{3}-\d{2}-\d{4}\b` with context keyword evaluation.
- **Cloud IAM Secrets & API Keys**: AWS Access Key pattern `AKIA[0-9A-Z]{16}`, GitHub tokens, and JWT assertions.
- **HIPAA Medical Records**: Patient MRN numbers and ICD-10 medical diagnostics.
