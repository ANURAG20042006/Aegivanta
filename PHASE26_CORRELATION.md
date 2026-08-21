# Aegivanta — Autonomous Multi-Domain Incident Correlation (Phase 26.4)

## Correlation Graph Architecture

The Autonomous Correlation Engine correlates signals across 6 distinct security domains:
- **Endpoint Telemetry**: Process execution trees, file creation, registry modifications
- **Network Telemetry**: Flow duration, byte asymmetry, periodic beaconing, DNS tunneling
- **Identity & Access**: Kerberos tickets, impossible travel, privilege escalation tokens
- **Threat Intelligence**: IOC feed reputation, threat actor campaigns, malware families
- **Zero-Trust Posture**: Device health score, patch state, EDR presence
- **Detection Rules**: Multi-signal AST rule evaluations and MITRE ATT&CK techniques

## Output Graph Structure
- **Nodes**: `THREAT_ACTOR`, `ENDPOINT_ASSET`, `IDENTITY_USER`, `PROCESS`, `THREAT_INTEL`, `INTERNAL_SERVER`, `POSTURE`
- **Edges**: `INITIAL_ACCESS_EXPLOIT`, `SPAWNED_PROCESS`, `LOGGED_ON_SESSION`, `LATERAL_MOVEMENT_PROBE`, `FEED_CORRELATION`, `POSTURE_EVALUATION`
- **Attributes**: Confidence score (0.0-1.0), attack stage classification, affected assets/users, recommended investigation path
