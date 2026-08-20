# AEGIVANTA — PHASE 18 THREAT HUNTING SPECIFICATION

## 1. Workbench Hunting Entities
The hunting workbench executes typed DSL queries across 11 core entity classes:
1. **IP Addresses**: External C2 nodes, scanning hosts, and internal pivot nodes.
2. **Domains / FQDNs**: DGA domains, fast-flux DNS, and spoofed hostnames.
3. **File Hashes**: SHA256, MD5, and malware signatures.
4. **User Identities**: Anomalous authentication, privilege escalation, and credential abuse.
5. **Process Executions**: Suspicious child processes and command-line execution tokens.
6. **Authentication Anomalies**: High-frequency failure bursts (T1110).
7. **DNS Telemetry**: Tunneling and high-entropy lookups.
8. **Network Flows**: Long-duration low-bandwidth beacons and anomalous outbound transfers.
9. **Lateral Movement**: Internal SMB/RPC probing across ports 445/135 (T1021).
10. **MITRE ATT&CK Techniques**: Tactical technique hunts across ingested detections.
11. **URL Paths**: Phishing lures and exploit payload URIs.

## 2. Execution Logging & Metrics
Every executed hunt records execution time, matching alert count, indicators found, and querying analyst ID.
