# PHASE 37 — AI SOC & UEBA API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/ai-soc-ueba/summary` | Consolidated AI SOC Autonomy & UEBA Posture Scorecard. |
| `GET` | `/api/v1/ai-soc-ueba/profiles` | List UEBA User & Entity Risk Profiles (URS). |
| `GET` | `/api/v1/ai-soc-ueba/investigations` | List autonomous AI SOC investigation cases. |
| `POST` | `/api/v1/ai-soc-ueba/investigations/trigger` | Trigger autonomous investigation on a security alert. |
| `POST` | `/api/v1/ai-soc-ueba/investigations/approve-action` | Approve and enforce a proposed AI containment action. |
| `GET` | `/api/v1/ai-soc-ueba/insider-threats` | List detected insider threat indicators. |
| `GET` | `/api/v1/ai-soc-ueba/decision-audits` | List AI decision reasoning traces and action audits. |
