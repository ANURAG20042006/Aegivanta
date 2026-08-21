# Phase 47: Executive Security Intelligence & CISO Posture — Data Models

## Overview
Phase 47 introduces enterprise models for CISO board reporting, cyber return on investment (ROI), and executive KPI snapshots.

## Models

### 1. `CISOBoardReport`
Table: `ciso_board_reports`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `VARCHAR(64)` | Primary Key (`ciso-rep-...`) |
| `tenant_id` | `VARCHAR(64)` | Multi-tenant isolation key |
| `report_period` | `VARCHAR(32)` | Quarter or custom period (e.g., `2026-Q3`) |
| `executive_summary` | `TEXT` | High-level executive overview |
| `mean_time_to_detect_seconds` | `FLOAT` | Measured MTTD in seconds |
| `mean_time_to_contain_seconds` | `FLOAT` | Measured MTTC in seconds |
| `critical_threats_blocked` | `INTEGER` | Total critical threat volume blocked |
| `compliance_framework_scores` | `JSON` | Dict of framework scores (`FedRAMP`, `ISO27001`, `SOC2`, etc.) |
| `strategic_recommendations` | `JSON` | List of strategic executive recommendations |
| `overall_posture_score` | `FLOAT` | Consolidated security score (0 - 100) |
| `generated_by` | `VARCHAR(64)` | Author / AI Engine |
| `created_at` | `DATETIME` | Timestamp of generation |

### 2. `CyberROIRecord`
Table: `cyber_roi_records`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `VARCHAR(64)` | Primary Key (`roi-...`) |
| `tenant_id` | `VARCHAR(64)` | Multi-tenant isolation key |
| `period` | `VARCHAR(32)` | Calculation period (e.g., `2026-Q3`) |
| `estimated_breach_cost_avoidance_usd` | `FLOAT` | Estimated financial loss avoided |
| `insurance_premium_reduction_usd` | `FLOAT` | Insurance savings realized |
| `labor_cost_savings_usd` | `FLOAT` | Automated triage/containment labor savings |
| `security_investment_cost_usd` | `FLOAT` | Total security budget invested |
| `net_roi_percentage` | `FLOAT` | Calculated net ROI percentage |
| `breach_likelihood_reduction_pct` | `FLOAT` | Statistical reduction in breach risk |
| `created_at` | `DATETIME` | Timestamp of calculation |

### 3. `ExecutiveKPISnapshot`
Table: `executive_kpi_snapshots`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `VARCHAR(64)` | Primary Key (`kpi-snap-...`) |
| `tenant_id` | `VARCHAR(64)` | Multi-tenant isolation key |
| `snapshot_week` | `VARCHAR(32)` | ISO week (e.g., `2026-W34`) |
| `threat_volume_total` | `INTEGER` | Total alerts received |
| `autonomous_containment_rate_pct` | `FLOAT` | Percentage contained autonomously |
| `avg_investigation_time_minutes` | `FLOAT` | Average triage & investigation time |
| `soc2_control_health_pct` | `FLOAT` | SOC 2 active control health score |
| `iso27001_control_health_pct` | `FLOAT` | ISO 27001 control health score |
| `created_at` | `DATETIME` | Timestamp of snapshot |
