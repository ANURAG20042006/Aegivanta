# PHASE 29 — SECRET SCANNER SPECIFICATION

## 1. Detection Patterns

- **AWS Access Keys**: `AKIA[0-9A-Z]{16}`
- **GitHub Personal Access Tokens**: `ghp_[0-9a-zA-Z]{36}`
- **JSON Web Tokens (JWT)**: `eyJ...` header signatures
- **Private RSA/EC Keys**: `-----BEGIN PRIVATE KEY-----`
- **Shannon Entropy Filter**: High-entropy strings (>4.5) flagged for credential leakage.
