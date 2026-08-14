# SentinelAI Phase 2 SOC Operational Runbook

## Core Workflows

### 1. Continuous Asset Health Monitoring

- **Access Route**: `/monitoring`
- **Target Configurations**: Add target URLs and expected response codes.
- **SSRF Hardening**: System blocks private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.0.0/16`, `::1`) unless specifically permitted in test environments.
- **Debouncing**:
  - `1 failure`: Health state becomes `DEGRADED`.
  - `3 consecutive failures`: Health state escalates to `DOWN` and triggers an automated `DoS_Service_Outage` alert and incident correlation event.

### 2. Threat Intelligence Management

- **Access Route**: `/threat-intel`
- **Supported Formats**: `ipv4`, `ipv6`, `domain`, `url`, `sha256`, `md5`.
- **Feed Ingestion**: Supports `static_list`, `generic_json`, and `generic_csv` feed providers.
- **Enrichment**: Matches source and destination IPs during telemetry ingestion without changing original feature vectors or model probabilities.

### 3. Behavioral Anomaly Detection & Baseline Tuning

- **Access Route**: `/analytics`
- **Statistical Model**: Online incremental updates (Welford's algorithm).
- **Cold-Start Guard**: Requires $\ge 5$ baseline observations before firing anomaly alerts.
- **Detection Trigger**: $|z| \ge 3.0\sigma$.
- **Severity Mapping**:
  - $|z| \ge 5.0\sigma$: `CRITICAL`
  - $|z| \ge 4.0\sigma$: `HIGH`
  - $|z| \ge 3.0\sigma$: `MEDIUM`
- **Explainability**: Every anomaly includes deterministic English rationale detailing metric name, observed value, baseline mean $\pm$ standard deviation, and relative fold change.

### 4. Incident Investigations & Playbook Execution

- **Access Route**: `/investigations`
- **Evidence Aggregation**: Automatically links alerts, network events, IOC matches, and behavioral anomalies.
- **MITRE ATT&CK Mapping**: Maps threat vectors to ATT&CK stages (`RECONNAISSANCE`, `INITIAL_ACCESS`, `EXECUTION`, `PERSISTENCE`, `LATERAL_MOVEMENT`, `EXFILTRATION`, `IMPACT`).
- **Playbook Safety**: Playbook executions default strictly to `is_dry_run = True` (Simulation Mode). Actions generate verifiable audit logs and append directly to the incident timeline without impacting live network hardware unless explicitly confirmed by authorized analysts.
