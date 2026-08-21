# PHASE 34 — RBVM DATA MODELS

## 1. Database Entities

1. **`VulnerabilityRecord` (`vulnerability_records`)**:
   - `id`, `tenant_id`, `cve_id`, `title`, `description`, `affected_component`, `cvss_v3_score`, `cvss_vector`, `epss_probability`, `epss_percentile`, `in_cisa_kev`, `ransomware_associated`, `associated_threat_actors`, `rbvm_composite_score`, `priority_level`, `affected_asset_count`, `remediation_status`, `published_at`, `last_updated_at`.
2. **`AssetVulnerabilityMapping` (`asset_vulnerability_mappings`)**:
   - `id`, `tenant_id`, `hostname`, `asset_criticality`, `ip_address`, `cve_id`, `port_service`, `sla_due_date`, `is_sla_breached`, `status`, `detected_at`.
3. **`VirtualPatchRule` (`virtual_patch_rules`)**:
   - `id`, `tenant_id`, `cve_id`, `rule_name`, `rule_type`, `rule_syntax`, `status`, `total_blocked_requests_count`, `deployed_at`.
4. **`RemediationCampaign` (`remediation_campaigns`)**:
   - `id`, `tenant_id`, `campaign_name`, `target_cves`, `owner_team`, `target_completion_date`, `total_targeted_assets`, `remediated_assets_count`, `status`, `created_at`.
