# PHASE 39 — PREDICTIVE INTELLIGENCE DATA MODELS

## 1. Database Entities

1. **`PredictiveThreatForecast` (`predictive_threat_forecasts`)**:
   - `id`, `tenant_id`, `threat_vector_title`, `target_asset_category`, `probability_score`, `predicted_impact_severity`, `forecast_horizon`, `confidence_score`, `evidence_features_summary`, `model_version`, `created_at`.
2. **`AdversarialVectorSimulation` (`adversarial_vector_simulations`)**:
   - `id`, `tenant_id`, `threat_scenario_title`, `initial_access_vector`, `predicted_escalation_pathway`, `estimated_blast_radius_nodes`, `mitigation_directive`, `created_at`.
3. **`ThreatHorizonIndicator` (`threat_horizon_indicators`)**:
   - `id`, `tenant_id`, `indicator_name`, `category`, `trajectory_trend`, `observed_global_sightings`, `last_updated_at`.
