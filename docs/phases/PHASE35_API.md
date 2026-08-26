# PHASE 35 — DLP API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/dlp-security/summary` | Consolidated DLP & DSPM Posture Scorecard and metrics. |
| `GET` | `/api/v1/dlp-security/policies` | List active sensitive data inspection policies. |
| `POST` | `/api/v1/dlp-security/inspect` | Inspect & sanitize raw payload text in real-time. |
| `GET` | `/api/v1/dlp-security/incidents` | List intercepted DLP exfiltration incidents. |
| `GET` | `/api/v1/dlp-security/tokens` | List active tokenization vault records. |
| `POST` | `/api/v1/dlp-security/tokens/tokenize` | Tokenize sensitive value into a format-preserving surrogate. |
| `POST` | `/api/v1/dlp-security/tokens/detokenize` | Reversibly detokenize a surrogate token (RBAC governed). |
| `GET` | `/api/v1/dlp-security/shadow-data` | List discovered cloud storage buckets and database assets. |
