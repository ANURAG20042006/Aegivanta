# PHASE 44 — SECURITY MARKETPLACE API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/marketplace/summary` | Consolidated Marketplace Posture Scorecard. |
| `GET` | `/api/v1/marketplace/packages` | List curated marketplace extension packages. |
| `POST` | `/api/v1/marketplace/publish` | Publish a new security extension package with signed hash. |
| `GET` | `/api/v1/marketplace/installed` | List active installed extensions for a tenant. |
| `POST` | `/api/v1/marketplace/install` | Install and hot-reload a security extension into the pipeline. |
| `POST` | `/api/v1/marketplace/uninstall` | Uninstall and deactivate a security extension. |
