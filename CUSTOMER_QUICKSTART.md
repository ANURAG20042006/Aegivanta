# AEGIVANTA — CUSTOMER QUICKSTART GUIDE

**Platform**: Aegivanta — Autonomous Cyber Defense & Security Operations Platform  
**Document Version**: 3.0.0  

---

## Welcome to Aegivanta!

Aegivanta is your complete, AI-native cyber defense platform. This quickstart guide walks you through logging in, inspecting live network telemetry, triaging threat alerts, and executing automated containment.

---

## 1. Accessing Your SOC Dashboard
1. Open your browser and navigate to **[http://localhost:5173](http://localhost:5173)** (or your production ingress domain).
2. Click any of the **Quick Demo Accounts** (Admin, Analyst, or Viewer) to auto-fill credentials, or enter your assigned username and password.
3. Click **ACCESS AEGIVANTA**.

---

## 2. Five Essential Workflows for SOC Teams

### Workflow 1: Real-Time Threat Stream & SOC Overview
- On the **Dashboard**, view live metric ribbons (Active Incidents, Critical Risk Score, Telemetry Ingestion Rate).
- Watch the **Live SOC Event Stream** update automatically as network flows arrive.

### Workflow 2: Inspecting Traffic & Explaining AI Predictions
- Navigate to **Inspect traffic** (`/prediction`).
- Upload a flow CSV or enter connection parameters manually.
- Review the **TreeSHAP Explainability Waterfall** showing exactly why the model classified the flow as malicious.

### Workflow 3: Threat Hunting & Hypothesis Testing
- Navigate to **Threat Hunting** (`/threat-hunting`).
- Run structured hunt queries (e.g., `attack_type:DDoS AND destination_port:80`).
- Pivot across IP entities to identify related attack indicators.

### Workflow 4: Visualizing Attack Graphs & Lateral Movement
- Navigate to **Threat Graph** (`/threat-graph`).
- Explore the interactive node graph to see how attackers move laterally across internal subnets.

### Workflow 5: One-Click SOAR Containment & Remediation
- When an active threat is identified, click **CONTAIN THREAT IP**.
- Select the containment playbook (e.g., `BLOCK_IP` or `ISOLATE_HOST`).
- Review the execution audit log and reverse anytime using **Rollback**.
