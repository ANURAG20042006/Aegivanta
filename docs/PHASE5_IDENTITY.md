# Aegivanta Phase 5 — Enterprise Identity & Session Management

## 1. Identity Capabilities

- **Session Management**: Every authenticated principal receives an indexed `session_token_hash`. Active sessions can be queried via `GET /api/v1/identity/sessions` and terminated via `DELETE /api/v1/identity/sessions/{id}`.
- **Suspicious Session Detection**: Anomalous IP switches or new device fingerprints are flagged with `is_suspicious=True`.
- **Concurrent Session Controls**: Organizations can configure a maximum concurrent session ceiling (default: 5).
