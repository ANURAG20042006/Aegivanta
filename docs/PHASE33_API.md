# PHASE 33 — DECEPTION TECHNOLOGY API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/deception/summary` | Consolidated Deception Readiness Scorecard & Metrics. |
| `GET` | `/api/v1/deception/honeypots` | List deployed honeypot decoys across corporate network. |
| `POST` | `/api/v1/deception/honeypots/deploy` | Deploy a new honeypot decoy into target VLAN/segment. |
| `GET` | `/api/v1/deception/canaries` | List active traceable canary tokens. |
| `POST` | `/api/v1/deception/canaries/generate` | Generate a new traceable canary token (AWS, Doc, DNS). |
| `POST` | `/api/v1/deception/canaries/trigger/{id}` | Process canary trip ping and generate high-fidelity incident. |
| `GET` | `/api/v1/deception/interactions` | List captured adversary interaction ledger and keystrokes. |
| `GET` | `/api/v1/deception/endpoint-lures` | List active endpoint deception lures. |
