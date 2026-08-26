# PHASE D — REAL INFRASTRUCTURE END-TO-END ARCHITECTURE AUDIT

**Audit Date**: August 26, 2026  
**Auditor**: Senior Software Architect & DevSecOps Engineer  
**Target Repository**: Aegivanta / SentinelAI  
**Phase**: Phase D — Real Infrastructure End-to-End Validation  

---

## 1. Executive Summary

This architecture audit details the complete operational telemetry pipeline of Aegivanta from raw PCAP capture parsing through ML inference, alert correlation, incident management, real-time WebSocket delivery, SOC UI rendering, human-in-the-loop SOAR approval, and immutable audit logging.

---

## 2. Complete End-to-End Telemetry & Action Chain

```
[ Raw Network PCAP / Capture File ]
                │
                ▼ (Native Binary Parser: Ethernet/IPv4/TCP/UDP)
[ PCAP Ingestion & Flow Extractor ]  ➔ (FlowAggregator: 5-Tuple, IAT, Directional Stats)
                │
                ▼ (30 Canonical ML Features)
[ Real ML Inference Engine ]        ➔ (LightGBM Champion Model + RealModelExplainer)
                │
                ▼ (Threat Detection Thresholds)
[ Alert Engine ]                     ➔ (Severity, MITRE Tactic/Technique Mapping)
                │
                ▼ (Temporal & Entity Correlation)
[ Incident Correlation Engine ]      ➔ (Dynamic Multi-Factor Risk Score, Attack Timeline)
                │
                ▼ (Tenant-Scoped Broadcast)
[ Real-Time WebSocket Backplane ]    ➔ (ConnectionManager: Scoped text frames)
                │
                ▼ (Live State Reactivity)
[ SOC Dashboard UI ]                 ➔ (Incident Command Center, MITRE ATT&CK Matrix)
                │
                ▼ (Level 2 Policy Mandate: Human-in-the-Loop)
[ SOAR Proposal & Approval Engine ]  ➔ (Blast Radius Calculation, RBAC Approval)
                │
                ▼ (Non-Destructive Containment)
[ Safe Remediation Action ]          ➔ (Audit Record, Quarantine Flag, Notification)
                │
                ▼ (Tamper-Evident SHA-256 Chaining)
[ Immutable Audit Trail ]            ➔ (ImmutableAuditService)
```

---

## 3. Subsystem Architecture Map

| Pipeline Stage | Implementation Module | Input Schema / Protocol | Output / Artifact | Trace Identifier |
| :--- | :--- | :--- | :--- | :--- |
| **PCAP Ingestion** | `backend/app/services/pcap_service.py` | Binary PCAP (`libpcap` / `pcapng`) | `List[RawPacket]` | `pcap_id` |
| **Flow Aggregator** | `FlowAggregator` in `pcap_service.py` | 5-tuple packet streams | `BidirectionalFlow` | `flow_id` |
| **Feature Extraction** | `extract_features_from_pcap` | Flow statistical moments | `PacketFeatureVector` (30 features) | `feature_record_id` |
| **ML Inference** | `backend/app/services/predict_service.py` | `numpy.ndarray` (30 float features) | Model classification + Probabilities | `prediction_id` |
| **Alert Engine** | `backend/app/models/alert.py` | Inference classification | `Alert` ORM model | `alert_id` |
| **Correlation Engine**| `backend/app/services/correlation_engine.py` | Incoming `Alert` stream | `Incident` + `IncidentTimelineEvent` | `correlation_id` / `incident_id` |
| **WebSocket** | `backend/app/api/v1/websockets.py` | `ConnectionManager.broadcast_event` | Authenticated JSON text frame | `websocket_event_id` |
| **SOAR Engine** | `backend/app/services/autonomous_response_service.py` | Policy Level 2 + Blast Radius | `ResponseApproval` | `response_id` |
| **Audit Trail** | `backend/app/services/immutable_audit_service.py` | `AuditEventType` record | `AuditLog` | `audit_event_id` |

---

## 4. Integrity & Anti-Bypass Directives

1. **Zero Mock Ingestion**: Ingestion must process raw binary PCAP headers and payload bytes through `NativePCAPParser`.
2. **Zero Injected Predictions**: Inference must invoke the authenticated `LightGBM` model artifact (`best_model.joblib`).
3. **Traceability Chain**: Every step must record and propagate the explicit lineage ID chain into `results/phase_d/e2e_trace.json`.

---
