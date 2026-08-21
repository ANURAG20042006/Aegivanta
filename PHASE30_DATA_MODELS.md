# PHASE 30 — AI/LLM SECURITY DATA MODELS

## 1. Database Entities

1. **`LLMGuardrailPolicy` (`llm_guardrail_policies`)**:
   - `id`, `tenant_id`, `policy_name`, `target_model_endpoint`, `enforcement_mode`, `block_prompt_injection`, `prompt_injection_threshold`, `redact_pii`, `block_system_prompt_leakage`, `sanitize_output_xss`, `max_tokens_per_prompt`, `is_active`, `created_at`.
2. **`LLMSecurityEvent` (`llm_security_events`)**:
   - `id`, `tenant_id`, `owasp_category`, `threat_title`, `source_user_principal`, `source_ip`, `raw_prompt_hash`, `redacted_prompt_snippet`, `risk_score`, `is_blocked`, `action_taken`, `detected_at`.
3. **`ShadowAIDiscoveryRecord` (`shadow_ai_discovery_records`)**:
   - `id`, `tenant_id`, `ai_tool_name`, `category`, `user_principal`, `endpoint_hostname`, `data_volume_mb`, `risk_rating`, `is_corporate_approved`, `is_blocked`, `first_seen_at`, `last_active_at`.
4. **`VectorDBAuditRecord` (`vectordb_audit_records`)**:
   - `id`, `tenant_id`, `db_type`, `collection_name`, `total_embeddings_count`, `is_tenant_isolated`, `has_unencrypted_embeddings`, `pii_exposure_detected`, `poisoning_anomaly_score`, `audit_status`, `audited_at`.
