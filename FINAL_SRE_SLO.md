# Aegivanta — Site Reliability Engineering (SRE) & Service Level Objectives (SLOs)

## Service Level Objectives (SLOs)

| Service Dimension | Target SLO | Measurement Window | Alert Trigger Threshold |
|---|---|---|---|
| **API Availability** | 99.95% | Rolling 30 days | Error rate > 0.05% over 5m |
| **API Ingestion P95 Latency** | < 120ms | Rolling 1 hour | P95 > 250ms over 10m |
| **Telemetry Ingestion Lag** | < 2.0s | Real-time | Redis Stream backlog > 10,000 |
| **ML Threat Inference P95** | < 15ms | Rolling 1 hour | P95 > 50ms over 5m |
| **SOAR Response Execution** | < 500ms | Real-time | Failure rate > 0.01% |
