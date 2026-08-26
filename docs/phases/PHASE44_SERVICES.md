# PHASE 44 — SECURITY MARKETPLACE SERVICES

## 1. Services Overview

| Service Name | Path | Purpose |
|--------------|------|---------|
| `MarketplaceCatalogService` | `backend/app/services/marketplace_catalog_service.py` | Catalog search, category filtering, package signature generation, and publisher verification. |
| `PackageInstallerService` | `backend/app/services/package_installer_service.py` | Sandboxed package installation, hot-reload ingestion, and uninstallation. |
| `MarketplacePostureService` | `backend/app/services/marketplace_posture_service.py` | Evaluates consolidated security marketplace scorecard metrics (0–100). |
