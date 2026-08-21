# PHASE 27 — CWPP INCIDENT RUNBOOK

## 1. Runtime Detection Handling

1. **Reverse Shell / Remote Command Execution**:
   - **Signal**: Interactive shell spawned from web tier container.
   - **Triage**: Inspect process tree, parent PID, and remote connection IP.
   - **Remediation**: Isolate Pod via NetworkPolicy or trigger Aegivanta Workload Containment API `/api/v1/cloud-security/cwpp/contain/{id}`.
2. **Crypto-Mining Activity**:
   - **Signal**: High CPU utilization with outbound stratum connections.
   - **Remediation**: Terminate mining process, revoke compromised container credentials, and redeploy immutable base image.
