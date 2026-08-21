# PHASE 37 — AI SOC & UEBA DATA MODELS

## 1. Database Entities

1. **`UEBAUserProfile` (`ueba_user_profiles`)**:
   - `id`, `tenant_id`, `user_email`, `department`, `peer_group`, `user_risk_score`, `risk_level`, `baseline_login_hours`, `baseline_daily_egress_mb`, `anomalous_indicators_count`, `active_anomalies`, `last_evaluated_at`.
2. **`AISOCInvestigation` (`ai_soc_investigations`)**:
   - `id`, `tenant_id`, `investigation_title`, `root_alert_id`, `lead_hypothesis`, `investigation_state`, `triage_verdict`, `confidence_score`, `collected_evidence_items`, `proposed_actions`, `created_at`, `resolved_at`.
3. **`InsiderThreatIndicator` (`insider_threat_indicators`)**:
   - `id`, `tenant_id`, `suspect_identity`, `anomaly_category`, `anomaly_magnitude_score`, `evidence_summary`, `detected_at`.
4. **`AISOCDecisionAudit` (`ai_soc_decision_audits`)**:
   - `id`, `tenant_id`, `investigation_id`, `proposed_action`, `impact_tier`, `requires_human_approval`, `approval_status`, `decision_reasoning_trace`, `acted_by`, `audited_at`.
