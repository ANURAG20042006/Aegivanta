# PHASE 36 — MICROSEGMENTATION DATA MODELS

## 1. Database Entities

1. **`ZTNAConnectorNode` (`ztna_connector_nodes`)**:
   - `id`, `tenant_id`, `connector_name`, `region`, `status`, `public_ip`, `private_overlay_cidr`, `active_client_sessions_count`, `total_bytes_tunneled_gb`, `version`, `last_heartbeat_at`.
2. **`MicrosegmentationPolicy` (`microsegmentation_policies`)**:
   - `id`, `tenant_id`, `policy_name`, `source_segment`, `destination_segment`, `protocol_port`, `enforcement_action`, `min_device_trust_score`, `is_active`, `total_evaluated_flows`, `created_at`.
3. **`ZTNAAccessSession` (`ztna_access_sessions`)**:
   - `id`, `tenant_id`, `user_email`, `device_id`, `connector_node_name`, `client_overlay_ip`, `target_application`, `current_trust_score`, `session_status`, `started_at`, `last_activity_at`.
4. **`LateralMovementBlockedAlert` (`lateral_movement_blocked_alerts`)**:
   - `id`, `tenant_id`, `source_workload`, `source_segment`, `target_workload`, `target_segment`, `attempted_port_protocol`, `interception_action`, `threat_classification`, `blocked_at`.
