# SentinelAI — Final Enterprise Platform Architecture

## Complete Phase 3 Production Architecture Specification

```
                    ┌─────────────────────────┐
                    │       SOC USERS         │
                    │ Admin / Analyst / Viewer│
                    └────────────┬────────────┘
                                 │
                         SOC COMMAND CENTER
                              (Phase 3.9)
                                 │
                 ┌───────────────▼───────────────┐
                 │       API / WebSocket         │
                 └───────────────┬───────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   INCIDENT MANAGEMENT    │
                    │       (Phase 3.6)       │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────▼────────────────────────┐
        │              DETECTION INTELLIGENCE             │
        │ ML + Rules + TI + Behavioral + Correlation     │
        │         (Phases 3.1 → 3.6 → 3.10)              │
        └────────────────────────┬────────────────────────┘
                                 │
                       ┌─────────▼─────────┐
                       │   ATTACK GRAPH    │
                       │    (Phase 3.5)    │
                       └─────────┬─────────┘
                                 │
                       ┌─────────▼─────────┐
                       │ THREAT HUNTING    │
                       │ INVESTIGATION     │
                       │    (Phase 3.8)    │
                       └─────────┬─────────┘
                                 │
                       ┌─────────▼─────────┐
                       │      SOAR         │
                       │ RESPONSE/ROLLBACK │
                       │    (Phase 3.7)    │
                       └─────────┬─────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │       DISTRIBUTED PIPELINE          │
              │ Redis Streams + Workers + PostgreSQL│
              │            (Phase 3.11)             │
              └──────────────────┬──────────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │        OBSERVABILITY / SRE          │
              │ Metrics + Logs + Traces + Alerts   │
              │            (Phase 3.12)             │
              └──────────────────┬──────────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │ GOVERNANCE + AUDIT + COMPLIANCE    │
              │            (Phase 3.13)             │
              └──────────────────┬──────────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │       DR / BACKUP / RECOVERY        │
              │            (Phase 3.14)             │
              └──────────────────┬──────────────────┘
                                 │
                       ┌─────────▼─────────┐
                       │ FINAL CERTIFICATION│
                       │    (Phase 3.15)    │
                       └───────────────────┘
```

---

## Subsystem Breakdown

1. **Telemetry & Ingestion Layer (Phase 3.1, 3.2)**:
   - High-throughput binary PCAP parsing and 5-tuple flow aggregation.
   - 30-feature extraction matching CICIDS2017 feature engineering contract.
   - Redis Streams distributed ingestion with consumer groups and atomic deduplication.

2. **Detection & Intelligence Layer (Phase 3.4, 3.6, 3.10)**:
   - CatBoost/LightGBM/Random Forest ML classification ($F_1 = 0.999$).
   - FastIOCCache sub-millisecond in-memory indicator matching.
   - 10 production correlation sliding-window rules.
   - Multi-signal ensemble scoring and concept drift monitoring.

3. **Graph & Investigation Layer (Phase 3.5, 3.8)**:
   - Multi-hop lateral movement path discovery and blast-radius estimation.
   - Whitelist-enforced safe Threat Hunting query DSL.
   - Complete Investigation Case state machine (`OPEN` $\to$ `CLOSED`).

4. **SOAR & Response Layer (Phase 3.7)**:
   - Policy-driven automated remediation actions.
   - Human-in-the-loop approval workflows with two-person rule option.
   - Safe rollback mechanisms and full action auditing.

5. **Distributed Platform & Observability (Phase 3.9, 3.11, 3.12, 3.13, 3.14)**:
   - React 18 + Vite SOC Command Center with live WebSocket event streaming.
   - Horizontal Pod Autoscaling (HPA) and worker role partitioning.
   - Prometheus metrics, structured JSON logging, and HMAC-chained tamper-evident audit logs.
   - Automated DR backups and cold-start restore procedures.
