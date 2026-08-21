# PHASE 39 — PREDICTIVE INTELLIGENCE API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/predictive-intel/summary` | Consolidated Predictive Security Intelligence Posture Scorecard. |
| `GET` | `/api/v1/predictive-intel/forecasts` | List emerging threat vector forecasts filtered by horizon. |
| `POST` | `/api/v1/predictive-intel/forecasts/generate` | Generate machine learning threat vector forecast. |
| `GET` | `/api/v1/predictive-intel/simulations` | List adversarial attack vector simulations with blast radius counts. |
| `GET` | `/api/v1/predictive-intel/horizon-indicators` | List global threat horizon trajectory indicators. |
