# PHASE 35 — CRYPTOGRAPHIC TOKENIZATION VAULT SPECIFICATION

## 1. Format-Preserving Encryption (FPE) Tokens

- Converts raw values into structured surrogates (e.g. `TKN-4111-XXXX-XXXX-9824` for cards, `TKN-XXX-XX-8924` for SSNs).
- Preserves downstream application schema compatibility while removing raw data exposure.
- Encrypts payload at rest using **AES-256-GCM**.
