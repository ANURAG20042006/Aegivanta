# PHASE 41 — FRONTEND EDGE SECURITY FABRIC COMMAND CENTER

## 1. UI Tabs

`EdgeFabricCenter.tsx` delivers 6 interactive enterprise tabs:
1. **Edge Fabric Overview**: Scorecard metrics, active edge PoP nodes, aggregate line-rate throughput, active connections, and replication latency.
2. **Global PoP Fleet**: Worldwide grid of edge PoP ingestion nodes with real-time throughput, active connections, and latency metrics.
3. **Edge Inspection & DDoS Policies**: Policy management table showing inspection modes (`SCRUB_DDOS`, `INLINE_BLOCK`), rate limits, and geo-fencing actions.
4. **Regional Ingestion WAN Routes**: Direct telemetry backhaul routes with protocol indicators (`WIREGUARD_MTLS`) and replication lag counters.
5. **Geo-Routing & Latency Map**: Worldwide latency topology and Anycast DNS routing breakdown.
6. **Deploy Edge Policy**: Interactive form to deploy line-rate packet inspection, DDoS scrubbing, and geo-fencing policies.
