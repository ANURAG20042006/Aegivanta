# PHASE 5 — BASELINE FRONTEND AUDIT

**Target Repository**: SentinelAI (`frontend/src/`)  
**Audit Timestamp**: 2026-08-13  
**Auditor**: Antigravity Frontend Engineering Team  

---

## Executive Summary

A comprehensive component-by-component frontend audit was performed inspecting React components, services, hooks, charts, and state management in `frontend/src/`.

---

## Baseline Audit Findings

### 1. Hardcoded Dashboard Counter Offsets & Mock Summaries
- **Location**: [`frontend/src/pages/Dashboard.tsx:L27-L36`](file:///c:/Users/NJ542WS/Desktop/major%20project/frontend/src/pages/Dashboard.tsx#L27)
- **Finding**: `Dashboard.tsx` added static base numbers `142850 + packets.length` and `1842 + alerts.length` to WebSocket packet counts, and hardcoded `mockThreatSummary` array (`DDoS: 46.1%`, `DoS Hulk: 22.8%`).
- **Required Action**: Replace static offsets with real data from `getAnalyticsSummary()` (`/api/v1/analytics/summary`).

### 2. Static Active Model Default Fallback
- **Location**: [`frontend/src/pages/Dashboard.tsx:L25`](file:///c:/Users/NJ542WS/Desktop/major%20project/frontend/src/pages/Dashboard.tsx#L25)
- **Finding**: Default active model was initialized as static string `'XGBoost v2.1'`.
- **Required Action**: Dynamically display the active model returned by `getHealthCheck()` or `getAnalyticsSummary()`.

### 3. Static Latency Indicator
- **Location**: [`frontend/src/pages/Dashboard.tsx:L128`](file:///c:/Users/NJ542WS/Desktop/major%20project/frontend/src/pages/Dashboard.tsx#L128)
- **Finding**: Stream latency was rendered as hardcoded string `"4.2 ms"`.
- **Required Action**: Display dynamic API/database latency from `/health` or `/metrics`.

### 4. Static Operating Mode Banner
- **Location**: [`frontend/src/pages/Dashboard.tsx:L63`](file:///c:/Users/NJ542WS/Desktop/major%20project/frontend/src/pages/Dashboard.tsx#L63)
- **Finding**: Operating mode was rendered as static pill badge `DEMO MODE (SYNTHETIC STREAM)` regardless of actual server operating mode.
- **Required Action**: Read `operating_mode` dynamically from backend `/health` endpoint (`DEMO`, `LAB`, `PRODUCTION`).

---

## Audit Component Matrix

| Page/Component | Feature | Issue Identified | Remediation Plan |
| :--- | :--- | :--- | :--- |
| `Dashboard.tsx` | Summary Cards | Static number offsets (`142850 + len`) | Bind to `analyticsService.getSummary()` |
| `Dashboard.tsx` | Operating Mode | Static `DEMO MODE` text | Bind to `health.operating_mode` |
| `Dashboard.tsx` | Active Model | Static `'XGBoost v2.1'` | Bind to `summary.active_model` |
| `Analytics.tsx` | ROC Curves | Mixed curves | Uses `/analytics/roc` with `CURRENT MODEL` tag |
| `Prediction.tsx` | Threat Single/Batch | Input Schema | Sends `PacketFeatureVector`, renders real SHAP |
| `History.tsx` | Incident Table | Incident List | Pagination via `/incidents` endpoint |
