# SentinelAI Phase 4 — SaaS Operations & Runbook

## 1. Operating Modes & Deployment Models

SentinelAI v4.0 supports four commercial deployment models:
1. **Multi-Tenant SaaS (Cloud)**: Multi-tenant database with strict `TenantContext` isolation and rate limiting.
2. **Private Cloud / VPC**: Dedicated Kubernetes cluster with isolated PostgreSQL and Redis instances.
3. **Enterprise Self-Hosted**: On-premises air-gapped deployment with local model weights and threat feeds.
4. **Managed SOC (MSSP)**: Multi-tenant portal allowing MSSP analysts to pivot between customer tenant workspaces.

---

## 2. Telemetry Ingestion & Sensor Operations

- Sensor Agents connect to `POST /api/v1/sensors/{id}/heartbeat` every 30 seconds.
- Heartbeats update sensor `ONLINE` status and report flow count statistics.
- If no heartbeat is received within 300 seconds, the sensor status transitions to `OFFLINE`.
- To revoke a sensor immediately, invoke `DELETE /api/v1/sensors/{id}`.
