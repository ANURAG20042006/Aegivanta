# PHASE 40 — FEDERATED THREAT SHARING DATA MODELS

## 1. Database Entities

1. **`FederatedIOCExchangeNode` (`federated_ioc_exchange_nodes`)**:
   - `id`, `tenant_id`, `node_pseudonym`, `trust_tier`, `consensus_weight`, `public_key_hash`, `status`, `created_at`.
2. **`FederatedThreatIndicator` (`federated_threat_indicators`)**:
   - `id`, `tenant_id`, `anonymized_indicator_hash`, `threat_classification`, `differential_privacy_epsilon`, `confidence_consensus_score`, `peer_validations_count`, `syndication_status`, `shared_at`.
3. **`HomomorphicMatchQuery` (`homomorphic_match_queries`)**:
   - `id`, `tenant_id`, `encrypted_query_hash`, `blind_match_status`, `execution_time_ms`, `queried_at`.
