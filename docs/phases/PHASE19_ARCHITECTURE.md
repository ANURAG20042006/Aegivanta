# AEGIVANTA — PHASE 19 PLATFORM ARCHITECTURE

## Autonomous SOC & SOAR 2.0 Layer

### 1. System Topology
Aegivanta Phase 19 introduces an enterprise-grade autonomous SOC orchestration layer coordinating declarative playbooks, human approval gating, emergency containment kill switches, and reversible action rollback.

```mermaid
graph TD
    A[Security Anomaly / Incident / Telemetry] --> B[SOAR 2.0 Decision Engine]
    B -->|Check Policy & Risk Score| C{Autonomy & Gating}
    C -->|Critical Asset / Low Conf| D[Human Approval Queue]
    C -->|High Conf & Permitted Policy| E[Emergency Kill Switch Check]
    E -->|Kill Switch ACTIVE| D
    E -->|Kill Switch DISARMED| F[SOAR Orchestration Runner]
    F -->|Step 1: Network Containment| G[Firewall Connector]
    F -->|Step 2: Endpoint Isolation| H[EDR / Sensor Connector]
    F -->|Step 3: Identity Revocation| I[IAM Connector]
    F -->|Snapshot Original State| J[Response Rollback Ledger]
    D -->|Analyst Approved| F
```

### 2. Core Pillars
- **Declarative Playbook Engine**: Structured JSON/YAML playbooks with syntax validation, dry-run simulation mode, and step-level execution tracking.
- **Explainable Multi-Factor Decision Engine**: Integrates asset criticality, alert severity, threat intelligence score, and ML confidence.
- **Human-In-The-Loop & Kill Switch**: Fast manual approval queues with a global emergency kill switch.
- **Reversible Containment & Rollback**: Automatic capture of pre-action state snapshots for zero-disruption recovery.
