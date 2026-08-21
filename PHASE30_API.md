# PHASE 30 — AI/LLM SECURITY API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/llm-security/summary` | Consolidated AI Security & OWASP Top 10 Scorecard. |
| `POST` | `/api/v1/llm-security/guardrails/inspect` | Inspect prompt through real-time firewall proxy. |
| `GET` | `/api/v1/llm-security/events` | List audit events for prompt injections and PII leaks. |
| `GET` | `/api/v1/llm-security/shadow-ai` | List discovered Shadow AI tools and employee usage. |
| `POST` | `/api/v1/llm-security/shadow-ai/block/{id}` | Block or unblock discovered Shadow AI applications. |
| `GET` | `/api/v1/llm-security/vectordb/audits` | List Vector DB security audit records. |
| `POST` | `/api/v1/llm-security/vectordb/scan` | Execute live security audit on a vector collection. |
