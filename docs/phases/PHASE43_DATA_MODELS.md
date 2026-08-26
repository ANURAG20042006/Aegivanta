# PHASE 43 — DATA GOVERNANCE & DSAR DATA MODELS

## 1. Database Entities

1. **`DataLineageRecord` (`data_lineage_records`)**:
   - `id`, `tenant_id`, `data_asset_name`, `pipeline_stage`, `transform_hash`, `upstream_asset_id`, `record_count`, `recorded_at`.
2. **`LegalHoldOrder` (`legal_hold_orders`)**:
   - `id`, `tenant_id`, `matter_reference`, `custodian_name`, `scope_pattern`, `status`, `frozen_artifact_count`, `issued_at`.
3. **`DSARPrivacyRequest` (`dsar_privacy_requests`)**:
   - `id`, `tenant_id`, `requester_email`, `request_type`, `status`, `discovered_records_count`, `completion_certificate_hash`, `requested_at`.
