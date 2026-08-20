# AEGIVANTA — SECURITY ANALYST OPERATIONAL GUIDE

**Platform**: Aegivanta — Autonomous Cyber Defense & Security Operations Platform  
**Target Audience**: Tier 1/2/3 Security Analysts, Incident Handlers, Threat Hunters  
**Document Version**: 3.0.0  

---

## 1. Alert Triage Lifecycle

When a new detection event fires, follow the standard Aegivanta triage process:

```
[NEW ALERT] ──> [INVESTIGATE] ──> [ATTACH EVIDENCE] ──> [EXECUTE SOAR] ──> [RESOLVE]
```

1. **Review Alert Details**: Navigate to **Live alerts** (`/alerts`). Click the alert to inspect flow 5-tuple, protocol, and classification confidence.
2. **Examine SHAP Explanations**: Click **Explain AI Decision** to view top contributing feature weights.
3. **Check IOC Reputation**: Query the Threat Intel database to check if the source IP or destination matches known botnets or command-and-control (C2) servers.

---

## 2. Investigation Case Management
1. Navigate to **Investigations** (`/investigations`).
2. Create an investigation case or attach the alert to an existing incident case.
3. Use **Threat Hunting** (`/threat-hunting`) to query related flows originating from the same subnet.
4. Document analyst findings in the case notes.

---

## 3. Incident Containment & SOAR Actions
1. Open the Incident Command panel.
2. If confirmed malicious, click **CONTAIN THREAT IP**.
3. Confirm the automated playbook (`BLOCK_IP` or `ISOLATE_HOST`).
4. Once contained, mark the incident status as `RESOLVED`.
