# SentinelAI SOC Operations Manual: Phase 1 Architecture & Workflows

## 1. Executive Operational Overview
SentinelAI is an enterprise-grade AI/ML Network Intrusion Detection and Security Operations Center (SOC) platform. **Phase 1** equips SOC tier-1, tier-2, and tier-3 analysts with an end-to-end incident management lifecycle:

```
[ Network Flow Telemetry / Ingress Sensor ]
                    │
                    ▼
[ ML Detection Pipeline (CatBoost Champion) ]
                    │
                    ▼
[ Protected Asset Resolution & Threat Risk Scoring ]
                    │
                    ▼
[ Deterministic Incident Correlation Engine ]
                    │
                    ▼
[ Chronological Attack Timeline & WebSocket Live Stream ]
                    │
                    ▼
[ Analyst Triage, State Transitions & Perimeter Containment ]
```

---

## 2. Protected Asset Management & Sensor Onboarding

### 2.1 Asset Entity Model
Monitored infrastructure assets are registered in SentinelAI with operational metadata:
- **Identifier & FQDN**: Unique UUID, Display Name, and Fully Qualified Domain Name (or hostname).
- **Network Resolution**: Bound Target IP address used by the correlation engine to match network flow destinations.
- **Asset Type**: `website`, `api`, `server`, `database`, `endpoint`, `network`, `other`.
- **Environment**: `production`, `staging`, `development`.
- **Criticality Tier**: `critical` (1.0), `high` (0.75), `medium` (0.5), `low` (0.25).
- **Operational Health**: `active`, `degraded`, `compromised`, `maintenance`, `inactive`.

### 2.2 Telemetry Integration Architecture
Protected assets feed network flow metrics (78 CICIDS2017 flow attributes) into SentinelAI via:
1. **Reverse Proxy Flow Logger (Nginx / Envoy / HAProxy)**: Exports flow summary metrics (duration, packet rates, byte distributions, SYN/ACK ratios) directly to `POST /api/v1/predict/single`.
2. **Suricata / Zeek Flow Mirror**: Captures raw packet streams on perimeter switch taps, computes flow vector metrics, and streams vectors to SentinelAI.
3. **Internal Agent Sensor**: Light daemon deployed on host endpoints submitting flow snapshots.

> [!IMPORTANT]
> SentinelAI does not execute unauthorized external web crawls. Ingress telemetry must originate from registered proxy logs, network sensors, or authenticated API submissions.

---

## 3. Dynamic Operational Risk Scoring Engine

### 3.1 Transparent Multi-Factor Formula
Unlike black-box machine learning probability scores, SentinelAI evaluates operational risk deterministically for SOC auditability:

$$\text{Operational Risk} = (\text{Severity Weight} \times 40.0) + (\text{Model Confidence} \times 25.0) + (\text{Asset Criticality} \times 20.0) + (\text{Recurrence Factor} \times 15.0)$$

Where:
$$\text{Recurrence Factor} = \min\left(1.0, \frac{\text{Alert Count}}{10.0}\right)$$

### 3.2 Component Weights & Scoring Matrix

| Component | Weight | Input Values & Normalized Factors |
|---|---|---|
| **Threat Severity** | **40%** | `Critical` = 1.0, `High` = 0.75, `Medium` = 0.50, `Low` = 0.25, `Info` = 0.05 |
| **Model Confidence** | **25%** | $0.0 \le \text{Confidence} \le 1.0$ (Defaults to 0.50 if model output is uncalibrated) |
| **Asset Criticality** | **20%** | `Critical` = 1.0, `High` = 0.75, `Medium` = 0.50, `Low` = 0.25 |
| **Recurrence / Frequency** | **15%** | $\min(1.0, \text{Alert Count} / 10.0)$ (Saturates at 10 correlated alerts) |

### 3.3 Risk Tiers

- **0.0 – 24.9 (`LOW`)**: Informational or low-impact anomalies; standard logging.
- **25.0 – 49.9 (`MEDIUM`)**: Suspicious flow pattern on non-critical asset; queued for routine triage.
- **50.0 – 74.9 (`HIGH`)**: High-confidence attack or threat against staging/production asset; analyst alert generated.
- **75.0 – 100.0 (`CRITICAL`)**: High/Critical severity attack on critical production infrastructure; immediate containment trigger.

---

## 4. Deterministic Incident Correlation & Severity Policy

### 4.1 Correlation Rules
Incoming alerts within a sliding **300-second (5 minute) correlation window** are automatically grouped into unified incidents if:
$$\left(\text{Asset ID Match} \lor \text{Destination IP Match}\right) \land \left(\text{Source IP Match} \lor \text{Attack Category Match}\right)$$

### 4.2 Explicit Incident Severity Policy
Incident severity is governed deterministically through:
$$\text{Incident Severity} = \max(\text{Current Severity}, \text{Incoming Alert Severity}, \text{Risk-Implied Severity})$$

1. **Monotonic Severity Guarantee**: An active incident's severity rank never automatically decreases as additional alerts correlate.
2. **Alert Severity Escalation**: If an incoming correlated alert has a higher discrete severity level, the incident severity immediately escalates.
3. **Risk-Threshold Escalation**:
   - $\text{Risk Score} \ge 80.0 \implies \text{Critical}$
   - $\text{Risk Score} \ge 60.0 \implies \text{High}$
   - $\text{Risk Score} \ge 40.0 \implies \text{Medium}$
   - $\text{Risk Score} < 40.0 \implies \text{Low}$

### 4.3 Correlation Lifecycle
1. **Existing Match Found**:
   - Increments incident `alert_count`.
   - Updates `last_seen` timestamp.
   - Recalculates multi-factor `risk_score`.
   - Evaluates and updates incident severity per the **Explicit Incident Severity Policy**.
   - Appends chronological `ALERT_CORRELATED` event to the attack timeline.
2. **No Active Match Found**:
   - Allocates unique incident code (`INC-XXXXXX`).
   - Assigns initial risk score, title, and initial severity from the root alert.
   - Appends root `DETECTION` event to the attack timeline.
   - Sets initial lifecycle state to `DETECTED`.

---

## 5. Protected Asset Lifecycle & Soft-Delete Preservation

To safeguard historical incident forensics, telemetry ledgers, and foreign key integrity, `DELETE /api/v1/assets/{id}` operates as a **soft-delete / deactivation**:
- Sets `asset.status = "inactive"`.
- Updates `asset.updated_at` to the current timestamp.
- Emits an auditable `AuditLog(action="DEACTIVATE_PROTECTED_ASSET")`.
- Preserves all historical alert relationships, incident correlation history, and timeline references without data or relation loss.

---

## 6. Feature Flag Configuration (`SOC_PHASE1_ENABLED`)

The Phase 1 SOC capabilities are protected by a dedicated feature flag in `backend/app/config.py`:
- `SOC_PHASE1_ENABLED=true` (default): Full dynamic SOC workflow enabled.
- `SOC_PHASE1_ENABLED=false`: Fallback mode routing flows through the pure ML baseline IDS pipeline without touching model weights, feature ordering, preprocessing, or explainability engines.

---

## 7. Incident Lifecycle & Chronological Attack Timeline

### 7.1 Verified State Machine Transition Matrix

```
[ DETECTED ] ──► [ TRIAGED ] ──► [ INVESTIGATING ] ──► [ CONTAINED ] ──► [ RESOLVED ] ──► [ CLOSED ]
                      │                                      ▲
                      └──► [ CLOSED (FP) ]                  │
                                                            │
                      [ INVESTIGATING ] ─────────────────────┘
```

- `DETECTED` $\rightarrow$ `TRIAGED`
- `TRIAGED` $\rightarrow$ `INVESTIGATING` or `CLOSED` (False Positive)
- `INVESTIGATING` $\rightarrow$ `CONTAINED` or `RESOLVED`
- `CONTAINED` $\rightarrow$ `RESOLVED`
- `RESOLVED` $\rightarrow$ `CLOSED`

### 7.2 Timeline Event Taxonomy
- `DETECTION`: Root ML inference detection and initial incident creation.
- `ALERT_CORRELATED`: Additional threat alert mapped to ongoing incident.
- `TRIAGE`: Analyst acknowledges and assigns priority.
- `STATUS_CHANGE`: Lifecycle progression along the state machine.
- `ANALYST_ACTION`: Manual analyst investigation notes and evidence uploads.
- `REMEDIATION`: Containment action dispatched (e.g. perimeter firewall IP block).
- `RESOLUTION`: Threat confirmed mitigated and incident signed off.

---

## 8. Real-Time WebSockets Telemetry

### 8.1 Endpoint: `/ws/threats`
Clients receive streaming JSON telemetry with standard event envelopes:

```json
{
  "type": "ALERT_TRIGGERED",
  "data": {
    "alert_id": "ALT-8F9E01AB",
    "incident_id": "848a3350-48e2-468e-9494-0cfb0e5fa3f0",
    "incident_code": "INC-791A08CE",
    "attack_type": "DDoS",
    "severity": "High",
    "confidence": 0.9421,
    "risk_score": 78.5,
    "source_ip": "192.168.1.105",
    "destination_ip": "10.0.0.1",
    "asset_name": "Primary Web Gateway",
    "timestamp": "2026-08-14T12:00:00Z"
  },
  "timestamp": 1786708800.0
}
```

---

## 9. Role-Based Access Control (RBAC) Matrix

| Action / Resource | Admin | Analyst / SOC Analyst | Viewer |
|---|:---:|:---:|:---:|
| View Dashboard, Topology, Analytics | ✅ | ✅ | ✅ |
| List & Inspect Protected Assets | ✅ | ✅ | ✅ |
| Register / Update Protected Assets | ✅ | ✅ | ❌ |
| Delete / Deactivate Protected Assets | ✅ | ❌ | ❌ |
| List & Filter Threat Alerts | ✅ | ✅ | ✅ |
| Triage & Update Alert Status | ✅ | ✅ | ❌ |
| View Incident Details & Attack Timeline | ✅ | ✅ | ✅ |
| Add Analyst Notes to Timeline | ✅ | ✅ | ❌ |
| Transition Incident State | ✅ | ✅ | ❌ |
| Execute Remediation / Threat Containment | ✅ | ✅ (Lab/Demo) / Admin (Prod) | ❌ |
