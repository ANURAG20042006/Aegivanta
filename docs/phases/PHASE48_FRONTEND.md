# Phase 48: AI/ML Model Platform — Frontend Documentation

## Component Overview
The AI/ML Model Platform Hub is implemented at `frontend/src/pages/MLModelPlatformCenter.tsx` and available on the `/ml-platform` route in the application router and Sidebar.

## Key Sections & Tabs

### 1. Header & Platform Metrics
- Summary cards for Total Registered Models, Production Champion Model accuracy & P99 latency, Statistical Drift Status (Stable/Drifting), and Adversarial Defenses Score (99.1%).
- "Simulate Attack Defense" modal action button.

### 2. Tabs
- **Model Registry Tab**: Lists all registered models (CatBoost, XGBoost, GNN, Transformer, IsolationForest) with champion badges, versioning, framework tags, accuracy metrics, and latency graphs.
- **Drift Monitoring Tab**: Displays PSI and KS-statistic indicators per feature, drift status chips, and automated retrain triggers.
- **Adversarial Defenses Tab**: Interactive timeline of blocked attacks (Evasion, Extraction, Membership Inference, Poisoning), defense latency badges, and defense mechanism tags.
