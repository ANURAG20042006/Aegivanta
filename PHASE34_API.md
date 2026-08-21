# PHASE 34 — RBVM API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/vulnerability-mgmt/summary` | Consolidated RBVM Posture Scorecard & SLA metrics. |
| `GET` | `/api/v1/vulnerability-mgmt/vulnerabilities` | List prioritized CVEs ranked by RBVM composite score and EPSS. |
| `GET` | `/api/v1/vulnerability-mgmt/asset-exposures` | List individual asset vulnerability instances with SLA countdowns. |
| `GET` | `/api/v1/vulnerability-mgmt/virtual-patches` | List active WAF/IPS virtual patches. |
| `POST` | `/api/v1/vulnerability-mgmt/virtual-patches/deploy` | Deploy an automated WAF/IPS virtual patch for a target CVE. |
| `GET` | `/api/v1/vulnerability-mgmt/campaigns` | List remediation campaigns and burn-down progress. |
| `GET` | `/api/v1/vulnerability-mgmt/epss-distribution` | Get EPSS 2.0 exploit probability distribution buckets. |
