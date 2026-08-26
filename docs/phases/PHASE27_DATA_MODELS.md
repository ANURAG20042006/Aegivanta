# PHASE 27 — CNAPP DATA MODELS

## 1. Database Entities

1. **`CloudAccount` (`cloud_accounts`)**:
   - `id`, `tenant_id`, `provider`, `account_name`, `account_identifier`, `environment`, `auth_type`, `encrypted_credentials`, `sync_status`, `health_status`, `discovered_assets_count`, `active_findings_count`, `last_synced_at`, `created_at`, `updated_at`.
2. **`CloudWorkloadFinding` (`cloud_workload_findings`)**:
   - `id`, `tenant_id`, `workload_type`, `workload_id`, `workload_name`, `host_ip`, `threat_type`, `severity`, `process_name`, `command_line`, `mitre_attack_technique`, `containment_status`, `is_contained`, `details`, `detected_at`.
3. **`ServerlessFunctionRisk` (`serverless_function_risks`)**:
   - `id`, `tenant_id`, `provider`, `function_arn`, `function_name`, `runtime`, `has_public_url`, `has_unencrypted_env_vars`, `has_wildcard_iam`, `vulnerable_dependencies_count`, `risk_score`, `remediation_advice`, `audited_at`.
4. **`KubernetesCluster` (`kubernetes_clusters`)**:
   - `id`, `tenant_id`, `cluster_name`, `distribution`, `k8s_version`, `node_count`, `pod_count`, `admission_controller_enforced`, `pod_security_standard`, `privileged_workloads_count`, `kspm_health_score`, `last_audited_at`.
