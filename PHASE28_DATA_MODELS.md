# PHASE 28 — ENTERPRISE IAM DATA MODELS

## 1. Database Entities

1. **`PAMSessionElevation` (`pam_session_elevations`)**:
   - `id`, `tenant_id`, `user_id`, `username`, `target_role`, `target_resource`, `justification`, `duration_minutes`, `status`, `approved_by`, `approved_at`, `expires_at`, `revoked_at`, `session_audit_log`, `created_at`.
2. **`IdentityThreatDetection` (`identity_threat_detections`)**:
   - `id`, `tenant_id`, `threat_type`, `target_username`, `source_ip`, `geo_location`, `severity`, `risk_score`, `mitre_attack_id`, `is_blocked`, `action_taken`, `evidence_details`, `detected_at`.
3. **`PasskeyCredential` (`passkey_credentials`)**:
   - `id`, `tenant_id`, `user_id`, `credential_id`, `public_key_pem`, `device_nickname`, `aaguid`, `sign_count`, `is_backup_eligible`, `last_used_at`, `created_at`.
4. **`IdentityScorecard` (`identity_scorecards`)**:
   - `id`, `tenant_id`, `user_id`, `username`, `identity_risk_score`, `risk_tier`, `is_dormant`, `last_login_days_ago`, `mfa_enabled`, `passkey_registered`, `has_excessive_privileges`, `assigned_roles`, `evaluated_at`.
