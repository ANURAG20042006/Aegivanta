# Phase 47: Executive Security Intelligence, Cyber ROI & CISO Posture Reporting — API Reference

## Base URL
`/api/v1/executive-intelligence`

## Endpoints

### 1. Executive Intelligence Posture Summary
`GET /api/v1/executive-intelligence/summary`
- **Description**: Returns consolidated executive scorecards including posture score, quarterly ROI, board report count, and weekly KPI status.
- **Security**: Requires tenant authentication and `ciso:read` or `executive:read` scope.
- **Response**: `200 OK`
```json
{
  "tenant_id": "tenant-enterprise-01",
  "overall_security_posture_score": 94.8,
  "quarterly_cyber_roi_percent": 1359.0,
  "net_value_delivered_usd": 665000.0,
  "total_ciso_reports": 4,
  "latest_ciso_report_id": "ciso-rep-2026-q3",
  "board_readiness_verdict": "EXECUTIVE_BOARD_APPROVED",
  "active_compliance_certifications": ["FedRAMP High", "ISO 27001", "SOC 2 Type II", "HIPAA"]
}
```

### 2. List CISO Board Reports
`GET /api/v1/executive-intelligence/reports`
- **Query Params**: `limit` (default 50), `offset` (default 0)
- **Response**: `200 OK` — List of `CISOBoardReport` records.

### 3. Get Latest CISO Board Report
`GET /api/v1/executive-intelligence/reports/latest`
- **Response**: `200 OK` — Latest `CISOBoardReport` with strategic recommendations and executive summary.

### 4. Generate On-Demand CISO Board Report
`POST /api/v1/executive-intelligence/reports/generate`
- **Request Body**:
```json
{
  "report_period": "2026-Q3",
  "custom_focus_areas": ["Zero Trust", "Autonomous Containment", "Cloud IAM"]
}
```
- **Response**: `201 Created` — Generated report with executive briefing and posture metrics.

### 5. List Cyber ROI Records
`GET /api/v1/executive-intelligence/roi`
- **Response**: `200 OK` — Historical ROI records.

### 6. Get Latest Cyber ROI Calculation
`GET /api/v1/executive-intelligence/roi/latest`
- **Response**: `200 OK` — Current ROI, breach likelihood reduction, and cost savings.

### 7. List Weekly Executive KPI Snapshots
`GET /api/v1/executive-intelligence/kpi-snapshots`
- **Response**: `200 OK` — Historical weekly KPI snapshots.
