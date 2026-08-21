# PHASE 35 — DLP DATA MODELS

## 1. Database Entities

1. **`DLPInspectionPolicy` (`dlp_inspection_policies`)**:
   - `id`, `tenant_id`, `policy_name`, `data_category`, `sensitivity_tier`, `regex_pattern`, `context_keywords`, `enforcement_action`, `is_enabled`, `total_violations_intercepted`, `created_at`.
2. **`DLPIncidentEvent` (`dlp_incident_events`)**:
   - `id`, `tenant_id`, `source_identity`, `channel`, `target_destination`, `matched_policy_name`, `data_category`, `masked_sample_snippet`, `violations_count`, `enforcement_action_taken`, `occurred_at`.
3. **`TokenizedDataVault` (`tokenized_data_vault`)**:
   - `id`, `tenant_id`, `token_identifier`, `surrogate_token_value`, `token_format`, `cipher_algorithm`, `encrypted_blob_payload`, `authorized_roles`, `times_detokenized`, `created_at`, `last_detokenized_at`.
4. **`ShadowDataStore` (`shadow_data_stores`)**:
   - `id`, `tenant_id`, `resource_uri`, `storage_provider`, `discovered_sensitive_records_count`, `detected_data_categories`, `encryption_state`, `risk_level`, `discovered_at`.
