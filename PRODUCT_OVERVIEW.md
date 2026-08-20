# AEGIVANTA — PRODUCT OVERVIEW

**Product Name**: Aegivanta  
**Tagline**: Autonomous Cyber Defense & Security Operations Platform  
**Version**: 3.0.0 (Enterprise Commercial Baseline)  
**License**: MIT / Commercial Enterprise Dual License  

---

## 1. Product Mission & Value Proposition

Aegivanta transforms network telemetry and security event streams into real-time, explainable, and autonomous cyber defense operations. Built for modern Enterprise SOC teams, Managed Detection and Response (MDR) providers, and critical infrastructure environments, Aegivanta unifies AI-driven intrusion detection, threat intelligence correlation, multi-hop attack graph analytics, and policy-governed SOAR remediation into a single pane of glass.

---

## 2. Core Platform Capabilities

```
       ┌────────────────────────────────────────────────────────┐
       │                AEGIVANTA SOC COMMAND CENTER            │
       │    [Live Telemetry] [Attack Graph] [MITRE ATT&CK Matrix]│
       └───────────────────────────┬────────────────────────────┘
                                   │
       ┌───────────────────────────┴────────────────────────────┐
       │               CORE ENGINE PIPELINE                     │
       ├─────────────────┬───────────────────┬──────────────────┤
       │  AI/ML ENGINE   │   THREAT INTEL    │   SOAR ENGINE    │
       │  • 12 Models    │   • IOC Cache     │   • Playbooks    │
       │  • CatBoost     │   • Feed Sync     │   • Containment  │
       │  • TreeSHAP XAI │   • Risk Scoring  │   • Safe Rollback│
       └─────────────────┴───────────────────┴──────────────────┘
```

### A. Research-Verified Machine Learning Engine
- **Champion Model**: CatBoost classifier trained on 30 benchmarked network flow features.
- **Explainable AI (XAI)**: Native TreeSHAP attribution generating per-flow feature contribution waterfall charts.
- **Model Governance**: Automated drift detection, challenger benchmark scoring, and SHA-256 integrity verification.

### B. Threat Intelligence & Deterministic Correlation
- **Fast IOC Cache**: In-memory Redis lookup matching IP addresses, domains, and SHA-256 file hashes in under 1.2ms.
- **Sliding-Window Correlation**: Multi-event temporal clustering grouping raw telemetry into structured incident cases.
- **Risk Scoring**: 0–100 deterministic risk engine incorporating severity, asset criticality, IOC reputation, and ML confidence.

### C. Multi-Hop Attack Graph & Lateral Movement Detection
- **Graph Topology**: Directed graph models linking source IPs, target assets, protocols, and observed MITRE ATT&CK techniques.
- **Blast Radius Analysis**: Graph traversal computing lateral movement reachability and affected blast radius.

### D. Autonomous SOAR & Safe Remediation
- **Supported Containment Actions**: `BLOCK_IP`, `ISOLATE_HOST`, `QUARANTINE_ASSET`, `REVOKE_SESSION`, `DISABLE_ACCOUNT`.
- **Safety First**: Dry-run simulation by default, granular RBAC approval workflows, zero shell execution, and one-click rollback.

---

## 3. Commercial Deployment Models

| Deployment Mode | Infrastructure | Scalability | Best For |
|---|---|---|---|
| **Community / Single Node** | Docker Compose / SQLite / Redis | Up to 5,000 eps | Lab, Demo, Small Dev Teams |
| **Enterprise Self-Hosted** | Kubernetes / PostgreSQL / Redis Cluster | Up to 100,000 eps | On-Premise Enterprise SOC |
| **Managed Cloud (SaaS)** | Cloud K8s (EKS/GKE/AKS) / Managed DB | 500,000+ eps | MSSP, MDR Providers, Multi-Tenant |

---

## 4. Commercial Feature Tiers

| Capability | Community (Free) | Professional | Enterprise |
|---|:---:|:---:|:---:|
| Core ML Threat Detection | ✅ Included | ✅ Included | ✅ Included |
| Real-time Telemetry & Alerts | ✅ Included | ✅ Included | ✅ Included |
| IOC Threat Feed Sync | 1 Feed | 5 Feeds | Unlimited Feeds |
| Attack Graph Analytics | Basic | Advanced | Multi-Hop + Blast Radius |
| SOAR Automated Response | Manual Only | Policy-Assisted | Fully Autonomous + Rollback |
| Role-Based Access Control | Admin / Viewer | Full RBAC | Custom Roles + SSO/SAML |
| High Availability & Autoscaling | ❌ | ❌ | HPA + Redis Cluster + PDB |
| Dedicated Enterprise SLA | Community | 24/5 Business | 24/7/365 Critical (15min) |
