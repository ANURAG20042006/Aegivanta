# PHASE 31 — ATTACK SURFACE & CTEM API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/attack-surface/summary` | Consolidated ASM & CTEM Exposure Scorecard. |
| `GET` | `/api/v1/attack-surface/assets` | List discovered external perimeter assets and open ports. |
| `POST` | `/api/v1/attack-surface/assets/discover` | Enroll and initiate discovery on new domain or IP. |
| `GET` | `/api/v1/attack-surface/dangling-dns` | List dangling DNS records vulnerable to subdomain takeover. |
| `GET` | `/api/v1/attack-surface/darkweb/credentials` | List compromised employee credentials in breach datasets. |
| `GET` | `/api/v1/attack-surface/brand/typosquats` | List brand lookalike domains and phishing alerts. |
| `GET` | `/api/v1/attack-surface/ctem/prioritized-exposures` | Return prioritized exposures mapped to Gartner CTEM stages. |
