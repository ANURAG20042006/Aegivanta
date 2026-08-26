# PHASE 35 — DETOKENIZATION RBAC GOVERNANCE SPECIFICATION

## 1. Access Control Matrix

| Role | Tokenize | Detokenize PCI Card | Detokenize PII SSN | Audit Access |
|:---|:---:|:---:|:---:|:---:|
| **admin** | Yes | Yes | Yes | Yes |
| **compliance_officer** | Yes | Yes | Yes | Yes |
| **security_analyst** | Yes | No | No | View Only |
| **viewer / guest** | No | No | No | No |
