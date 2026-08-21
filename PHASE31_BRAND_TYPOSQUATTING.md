# PHASE 31 — BRAND PROTECTION & TYPOSQUATTING SPECIFICATION

## 1. Lookalike Detection Algorithms

- **Levenshtein Distance**: Identifies character insertions, substitutions, and deletions (e.g. `aeglvanta.io` vs `aegivanta.io`).
- **Punycode & Homoglyph Analysis**: Identifies Cyrillic/Greek lookalike characters.
- **MX Record Verification**: Verifies whether fraudulent domain is configured to receive and send phishing emails.
