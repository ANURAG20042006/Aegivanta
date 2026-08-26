# Aegivanta Enterprise Cybersecurity SaaS Platform — Final Architecture Snapshot (v25.0.0)

## 1. Executive Platform Architecture

**Aegivanta** is an enterprise-grade AI-powered Autonomous Cybersecurity & Extended Detection and Response (XDR/SOC) SaaS platform designed for multi-tenant, cloud-native global scale.

```
+---------------------------------------------------------------------------------------------------+
|                                      AEGIVANTA CUSTOMER EDGE                                      |
|                                                                                                   |
|  [ React 18 / TypeScript Web Portal ]  [ Enterprise SSO / SCIM ]  [ Sensor Fleet: Linux/Win/K8s ] |
|  [ Endpoint XDR Agents ]               [ Cloud & Container Sensors ]  [ Integration Ecosystem ]   |
+------------------------------------------+--------------------------------------------------------+
                                           | (TLS 1.3 / Gzip Stream / HMAC Webhooks)
                                           v
+---------------------------------------------------------------------------------------------------+
|                                 GLOBAL INGESTION & ACCESS GATEWAY                                 |
|                                                                                                   |
|  - Rate Limiting & Sliding Window Quotas       - Mutual Sensor Token Verification                 |
|  - Multi-Tenant RBAC & Entitlement Gate        - Gzip/Zlib Decompression (Max 10MB Bound)          |
|  - Schema Validation (Flows, Auth, DNS, HTTP)  - Sliding LRU Deduplication (50k event window)     |
|  - Normalized Event Bus & Contract Router      - Webhook Replay Protection (HMAC-SHA256 Nonces)   |
+------------------------------------------+--------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------------------+
|                                DISTRIBUTED STREAMING & WORKER PLANE                               |
|                                                                                                   |
|  [ Redis Streams: telemetry:stream ] ---> [ Distributed Workers Pool (K8s HPA Autoscaling) ]      |
|                                           |                                                       |
|                                           +---> [ Multi-Model ML Inference: Supervised/Anomaly ]  |
|                                           +---> [ EDR & Behavioral Telemetry Analysis ]           |
|                                           +---> [ CSPM / KSPM / CIEM Cloud Security Scanners ]    |
|                                           +---> [ Threat Intelligence Normalization & Graph ]     |
|                                           +---> [ Attack Graph & Lateral Movement Engine ]        |
|                                           +---> [ Detection-as-Code Rule Evaluator ]              |
|                                           +---> [ Zero-Trust Device Posture Scoring Engine ]      |
+------------------------------------------+--------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------------------+
|                              DECISION, AI & AUTONOMOUS SOAR PLANE                                 |
|                                                                                                   |
|  - Incident Correlation & Dynamic Risk Scoring (0–100)                                            |
|  - Aegivanta AI Security Copilot 2.0 (Attack Path Reasoning & Evidence Synthesis)                 |
|  - Autonomous SOAR 2.0 (IP Block, Host Isolation, Kill Switches, Approval Gates, Rollback)        |
|  - Multi-Model Governance & Drift Tracking (Champion/Challenger Promotion, Lineage)               |
|  - Adversarial AI Defense (Prompt Injection & Model Abuse Shields)                                |
+------------------------------------------+--------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------------------+
|                              GOVERNANCE, AUDIT & PERSISTENCE PLANE                                |
|                                                                                                   |
|  [ PostgreSQL (Multi-Tenant Schemas) ]    [ Immutable Tamper-Evident Audit Hash-Chain ]           |
|  [ Compliance Posture Engine (SOC 2, ISO 27001, GDPR, NIST CSF, CIS Controls) ]                  |
|  [ Automated Disaster Recovery & Integrity Verification Engine (RPO < 5m, RTO < 15m) ]             |
|  [ FinOps & Capacity Engine (Tenant-Aware Unit Economics, SLO Error Budget Tracking) ]            |
|  [ 17+ Ecosystem Connectors (SIEM, SOAR, EDR, IAM, Ticketing, Messaging, Dead-Letter Queue) ]     |
+---------------------------------------------------------------------------------------------------+
```
