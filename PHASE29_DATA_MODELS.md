# PHASE 29 — SUPPLY CHAIN DATA MODELS

## 1. Database Entities

1. **`SBOMCatalogItem` (`sbom_catalog_items`)**:
   - `id`, `tenant_id`, `package_name`, `version`, `purl`, `ecosystem`, `is_direct_dependency`, `license_spdx_id`, `is_copyleft`, `vulnerability_count`, `critical_cve_count`, `high_cve_count`, `cve_identifiers`, `supplier_name`, `sha256_checksum`, `created_at`.
2. **`VEXStatement` (`vex_statements`)**:
   - `id`, `tenant_id`, `vulnerability_id`, `product_purl`, `status`, `justification`, `impact_statement`, `author`, `published_at`.
3. **`SLSAPipelineAttestation` (`slsa_pipeline_attestations`)**:
   - `id`, `tenant_id`, `artifact_name`, `artifact_digest`, `slsa_level`, `builder_id`, `build_invocation_id`, `cosign_signature`, `is_signature_verified`, `source_repo_uri`, `source_commit_sha`, `materials`, `created_at`.
4. **`PipelineSecurityGate` (`pipeline_security_gates`)**:
   - `id`, `tenant_id`, `gate_name`, `target_environment`, `enforcement_mode`, `max_critical_cves`, `max_high_cves`, `require_slsa_level_3`, `disallow_copyleft_licenses`, `require_secret_scan_clean`, `is_active`, `created_at`.
