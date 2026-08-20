# SentinelAI — Phase 3.6 Incident Response & Lifecycle Guide

## 1. Incident Lifecycle Finite State Machine

SentinelAI enforces strict, audit-logged lifecycle transitions across all recorded security incidents.

```
       +--------------+
       |     OPEN     |<-------------------------+ (Re-open)
       +-------+------+                          |
               |                                 |
               +------------------>+             |
               v                   v             |
        +--------------+    +--------------+     |
        |   TRIAGED    |--->| INVESTIGATING|     |
        +-------+------+    +-------+------+     |
                |                   |            |
                |                   v            |
                |           +--------------+     |
                |           |  CONTAINED   |     |
                |           +-------+------+     |
                |                   |            |
                v                   v            |
        +--------------+    +--------------+     |
        |FALSE_POSITIVE|    |   RESOLVED   |     |
        +-------+------+    +-------+------+     |
                |                   |            |
                +--------+ +--------+            |
                         v v                     |
                   +-------------+               |
                   |   CLOSED    +---------------+
                   +-------------+
```

---

## 2. Incident Operations API Endpoints

| Method | Path | Required Role | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/incidents/correlate` | `admin`, `analyst`, `viewer` | Ingests and correlates raw events or unaggregated alerts. |
| `GET` | `/api/v1/incidents` | `admin`, `analyst`, `viewer` | Paginated search and multi-criteria incident filtering. |
| `GET` | `/api/v1/incidents/{id}` | `admin`, `analyst`, `viewer` | Detailed incident record with associated telemetry & timeline. |
| `GET` | `/api/v1/incidents/{id}/timeline` | `admin`, `analyst`, `viewer` | Reconstructed chronological investigation timeline. |
| `GET` | `/api/v1/incidents/{id}/risk` | `admin`, `analyst`, `viewer` | Explainable multi-dimensional risk score breakdown. |
| `GET` | `/api/v1/incidents/{id}/evidence` | `admin`, `analyst`, `viewer` | Underlying forensic telemetry payload and indicators. |
| `GET` | `/api/v1/incidents/mitre-coverage` | `admin`, `analyst`, `viewer` | MITRE ATT&CK enterprise matrix coverage statistics. |
| `GET` | `/api/v1/incidents/statistics` | `admin`, `analyst`, `viewer` | Real-time incident counts by status, severity, and attack type. |
| `POST` | `/api/v1/incidents/{id}/assign` | `admin`, `analyst` | Assigns an analyst to lead the incident investigation. |
| `POST` | `/api/v1/incidents/{id}/status` | `admin`, `analyst` | Updates status with state-machine transition validation. |
| `POST` | `/api/v1/incidents/{id}/resolve` | `admin`, `analyst` | Formally resolves incident with remediation and root-cause notes. |

---

## 3. Risk-Based Alert Prioritization Formula

$$\text{Risk} = \min\left(100, \; 0.35 \cdot S_{\text{sev}} + 0.15 \cdot S_{\text{conf}} + 0.15 \cdot S_{\text{ioc}} + 0.15 \cdot S_{\text{asset}} + 0.10 \cdot S_{\text{lateral}} + 0.10 \cdot S_{\text{blast}} + \Delta_{\text{freq}} + \Delta_{\text{burst}}\right)$$

- **0–24**: `LOW`
- **25–49**: `MEDIUM`
- **50–74**: `HIGH`
- **75–100**: `CRITICAL`
