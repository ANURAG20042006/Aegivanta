# SentinelAI Enterprise Development Roadmap

This document outlines the systematic engineering roadmap for SentinelAI, broken down into 12 execution modules.

---

## Roadmap Overview

```
[Module 1: Scaffolding & Arch] ---> [Module 2: Specs & Schema] ---> [Module 3: Database & ORM]
                                                                            |
[Module 6: Backend REST API]  <--- [Module 5: ML/DL Engine]   <--- [Module 4: Auth & RBAC]
            |
[Module 7: WebSockets Feed]   ---> [Module 8: React Foundation]---> [Module 9: Dashboard Pages]
                                                                            |
[Module 12: Docs & Testing]   <--- [Module 11: Docker/DevOps]  <--- [Module 10: Export Engine]
```

---

## Module Milestone Breakdown

### Module 1: Project Architecture & Folder Scaffolding (CURRENT MODULE)
- **Deliverables**: Root workspace structure, `.gitignore`, `.env.example`, `LICENSE`, `requirements.txt`, `package.json`, `tsconfig.json`, `tailwind.config.js`, `vite.config.ts`, Architecture spec, Database design spec, UML diagrams, Development roadmap.
- **Verification**: Complete folder tree validation and configuration file check.

### Module 2: System Architecture & Data Schema Specification
- **Deliverables**: In-depth API contracts, Pydantic schemas for CICIDS2017 features, design patterns specification.

### Module 3: Database & ORM Engine
- **Deliverables**: PostgreSQL initial SQL scripts (`init.sql`, `schema.sql`, `seed.sql`), SQLAlchemy 2.0 Async ORM models, Redis connection layer.

### Module 4: Authentication & Security Core
- **Deliverables**: JWT token generator, password hashing, RBAC middleware, User management services.

### Module 5: Machine Learning & Deep Learning Engine
- **Deliverables**: CICIDS2017 schema definition, synthetic benchmark generator, cleaning/scaling/SMOTE preprocessor, 12 model classes, automated model selector, SHAP/LIME explainability engine, model artifact saver.

### Module 6: FastAPI Backend Core & REST Endpoints
- **Deliverables**: FastAPI main application, router endpoints for Auth, Predictions, Training, Analytics, Users, Logs.

### Module 7: Real-Time Telemetry & WebSockets
- **Deliverables**: WebSocket connection manager, packet stream simulator, real-time threat alert push system.

### Module 8: Frontend Application Foundation & Dark UI Design System
- **Deliverables**: React SPA setup, Tailwind CSS custom dark theme, layout shell (Sidebar, Navbar), authentication context, notification toast system.

### Module 9: Enterprise Dashboard & Visualization Pages
- **Deliverables**: Dashboard page, Analytics page (Heatmaps, ROC, Confusion Matrix, SHAP), Prediction page (CSV inspector & score visualizer), History, Users, Settings, About pages.

### Module 10: Report Generation Engine
- **Deliverables**: PDF executive report generator (ReportLab), Excel export engine (OpenPyXL), CSV downloader.

### Module 11: Containerization & DevOps Pipeline
- **Deliverables**: `Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.yml`, GitHub Actions workflow.

### Module 12: Comprehensive Documentation & Test Suite
- **Deliverables**: Pytest suite for backend and ML, `README.md` with badges, User Manual, Deployment Guide.
