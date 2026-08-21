# PHASE 41 — EDGE SECURITY FABRIC DATA MODELS

## 1. Database Entities

1. **`GlobalEdgePoPNode` (`global_edge_pop_nodes`)**:
   - `id`, `tenant_id`, `region_code`, `pop_location_name`, `edge_status`, `throughput_gbps`, `active_connections`, `latency_ms`, `last_heartbeat`.
2. **`EdgeInspectionPolicy` (`edge_inspection_policies`)**:
   - `id`, `tenant_id`, `policy_name`, `inspection_mode`, `edge_rate_limit_rps`, `geo_fence_action`, `enabled`, `created_at`.
3. **`RegionalIngestionRoute` (`regional_ingestion_routes`)**:
   - `id`, `tenant_id`, `source_region`, `target_core_cluster`, `routing_protocol`, `replication_lag_ms`, `is_primary`, `updated_at`.
