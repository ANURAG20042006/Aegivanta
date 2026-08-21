# PHASE 32 — CTI 2.0 DATA MODELS

## 1. Database Entities

1. **`ThreatActorProfile` (`threat_actor_profiles`)**:
   - `id`, `tenant_id`, `actor_name`, `aliases`, `country_of_origin`, `actor_type`, `primary_motivation`, `sophistication_level`, `diamond_adversary`, `diamond_capability`, `diamond_infrastructure`, `diamond_victimology`, `targeted_sectors`, `primary_mitre_techniques`, `is_active`, `last_seen_at`, `created_at`.
2. **`STIXFeedSource` (`stix_feed_sources`)**:
   - `id`, `tenant_id`, `feed_name`, `taxii_server_url`, `collection_id`, `feed_format`, `poll_interval_minutes`, `feed_reputation_score`, `auto_ingest_enabled`, `total_indicators_ingested`, `last_poll_status`, `last_polled_at`.
3. **`CTIIndicatorRecord` (`cti_indicator_records`)**:
   - `id`, `tenant_id`, `indicator_type`, `indicator_value`, `stix_pattern`, `threat_actor`, `malware_family`, `initial_confidence_score`, `current_confidence_score`, `decay_halflife_days`, `sighting_count`, `is_revoked`, `first_observed_at`, `last_sighted_at`.
4. **`CampaignHeatmapItem` (`campaign_heatmap_items`)**:
   - `id`, `tenant_id`, `campaign_name`, `threat_actor`, `tactic_name`, `mitre_technique_id`, `technique_name`, `heat_level`, `confidence_score`, `recorded_at`.
