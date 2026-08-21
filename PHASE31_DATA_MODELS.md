# PHASE 31 — ATTACK SURFACE DATA MODELS

## 1. Database Entities

1. **`ExternalAsset` (`external_assets`)**:
   - `id`, `tenant_id`, `fqdn_or_ip`, `asset_type`, `primary_ip`, `asn_organization`, `cloud_provider`, `open_ports`, `ssl_issuer`, `ssl_days_until_expiry`, `ssl_has_weak_ciphers`, `risk_score`, `status`, `first_discovered_at`, `last_scanned_at`.
2. **`DanglingDNSRisk` (`dangling_dns_risks`)**:
   - `id`, `tenant_id`, `subdomain`, `cname_target`, `target_service`, `takeover_risk_score`, `is_takeover_verified`, `status`, `detected_at`.
3. **`DarkWebCredentialLeak` (`darkweb_credential_leaks`)**:
   - `id`, `tenant_id`, `employee_email`, `breach_source`, `password_hash_sample`, `is_plaintext_exposed`, `severity`, `is_remediated`, `discovered_at`.
4. **`BrandImpersonationAlert` (`brand_impersonation_alerts`)**:
   - `id`, `tenant_id`, `impersonating_domain`, `levenshtein_similarity_score`, `registrar_name`, `has_active_mx_records`, `has_live_web_server`, `threat_status`, `detected_at`.
