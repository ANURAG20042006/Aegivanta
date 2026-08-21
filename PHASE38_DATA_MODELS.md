# PHASE 38 — DETECTION ENGINEERING & COMPLIANCE DATA MODELS

## 1. Database Entities

1. **`AutonomousDetectionRule` (`autonomous_detection_rules`)**:
   - `id`, `tenant_id`, `rule_name`, `rule_type`, `mitre_technique_id`, `rule_syntax_payload`, `lifecycle_state`, `noise_score`, `true_positive_rate_pct`, `evaluated_telemetry_count`, `created_at`.
2. **`ComplianceFrameworkControl` (`compliance_framework_controls`)**:
   - `id`, `tenant_id`, `framework`, `control_id`, `control_title`, `compliance_status`, `automated_evidence_summary`, `drift_details`, `last_assessed_at`.
3. **`ComplianceAuditReport` (`compliance_audit_reports`)**:
   - `id`, `tenant_id`, `framework`, `overall_compliance_score`, `passing_controls_count`, `failing_controls_count`, `auditor_attestation_hash`, `generated_by`, `generated_at`.
4. **`DetectionSandboxExecution` (`detection_sandbox_executions`)**:
   - `id`, `tenant_id`, `rule_id`, `test_event_payload`, `match_status`, `execution_time_ms`, `is_false_positive`, `evaluated_at`.
