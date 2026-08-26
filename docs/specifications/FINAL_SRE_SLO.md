# Aegivanta — Site Reliability Engineering (SRE) & Service Level Objectives (SLOs) (v25.0.0)

## Service Level Objectives (SLOs) & Error Budgets

| Service Dimension | Target SLO | Measurement Window | Alert Trigger Threshold | Current Measured |
|---|---|---|---|:---:|
| **API Availability** | 99.95% | Rolling 30 days | Error rate > 0.05% over 5m | 🟢 99.98% |
| **API Ingestion P95 Latency** | < 120ms | Rolling 1 hour | P95 > 250ms over 10m | 🟢 42ms |
| **Telemetry Ingestion Lag** | < 2.0s | Real-time | Redis Stream backlog > 10,000 | 🟢 0.25s |
| **ML Threat Inference P95** | < 15ms | Rolling 1 hour | P95 > 50ms over 5m | 🟢 6.2ms |
| **SOAR Response Execution** | < 500ms | Real-time | Failure rate > 0.01% | 🟢 85ms |
| **Disaster Recovery RPO** | < 5 min | Continuous | Replication lag > 60s | 🟢 < 1 min |
| **Disaster Recovery RTO** | < 15 min | Test drills | Recovery drill > 10m | 🟢 3.5 min |
