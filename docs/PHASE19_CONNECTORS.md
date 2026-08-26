# AEGIVANTA — PHASE 19 SOAR CONNECTORS SPECIFICATION

## 1. Supported Connector Ecosystem
- **Firewall & Network**: Palo Alto Next-Gen Firewall, Fortinet, AWS Security Groups, iptables.
- **Endpoint Detection & Response (EDR)**: CrowdStrike Falcon, SentinelOne, Microsoft Defender for Endpoint, Aegivanta Sensor Fleet.
- **Identity & Access Management (IAM)**: Okta Enterprise Directory, Azure Active Directory, AWS Cognito.
- **Ticketing & SIEM**: ServiceNow SecOps, Jira Service Management, Splunk, Generic Webhook.

## 2. Health Monitoring & Latency
Connectors maintain continuous heartbeat telemetry, logging latency into Prometheus and alerting when health degrades.
