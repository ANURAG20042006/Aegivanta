# AEGIVANTA — PHASE 18 OPERATIONS & RUNBOOK

## 1. Threat Feed Synchronization
Threat feed sync tasks execute via asynchronous worker jobs, logging sync duration into Prometheus histogram `aegivanta_threat_feed_sync_duration_seconds`.

## 2. Capacity & Query Limits
Analyst workbench hunts are strictly bounded by `limit` parameters (max 100 results per page) to preserve database read replica performance.
