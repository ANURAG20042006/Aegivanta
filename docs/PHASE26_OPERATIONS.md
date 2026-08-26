# Aegivanta — Autonomous SOC Operations Runbook (Phase 26.14)

## Operational Workflows

### 1. Incident Triage & Automated Investigation
1. Telemetry triggers automated AST rules or CatBoost/LSTM multi-modal detection models.
2. The Autonomous Correlation Engine builds an explainable multi-domain graph topology.
3. The Multi-Factor Incident Risk Engine scores the incident (0–100) across 11 contextual factors.
4. An automated SOC Case is created in `OPEN` state with SLA timers and lead analyst routing.

### 2. Threat Hunting Workbench V2
1. Analysts execute parameterized hunt templates against multi-terabyte normalized telemetry streams.
2. Match results are linked directly to investigation sessions and forensic cases.

### 3. Continuous Security Validation Runs
- Executed on a weekly cron schedule and triggered automatically upon pipeline deployment.
- Verifies all 16 security control domains with immediate remediation notifications.
