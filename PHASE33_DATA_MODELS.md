# PHASE 33 — DECEPTION DATA MODELS

## 1. Database Entities

1. **`HoneypotNode` (`honeypot_nodes`)**:
   - `id`, `tenant_id`, `node_name`, `decoy_type`, `internal_ip`, `vlan_segment`, `emulation_profile`, `interaction_level`, `total_hits_count`, `is_active`, `status`, `deployed_at`, `last_triggered_at`.
2. **`CanaryToken` (`canary_tokens`)**:
   - `id`, `tenant_id`, `token_type`, `token_name`, `token_value_preview`, `trigger_url_or_domain`, `placement_description`, `times_triggered`, `is_revoked`, `created_at`, `last_triggered_at`.
3. **`DeceptionInteractionEvent` (`deception_interaction_events`)**:
   - `id`, `tenant_id`, `source_ip`, `attacker_asn`, `target_decoy_name`, `interaction_type`, `captured_payload_or_command`, `mitre_engage_activity`, `fidelity_confidence`, `containment_action_taken`, `occurred_at`.
4. **`EndpointLureDeployment` (`endpoint_lure_deployments`)**:
   - `id`, `tenant_id`, `endpoint_hostname`, `lure_type`, `target_honey_user`, `deployment_status`, `last_verified_at`.
