# Aegivanta Enterprise Cybersecurity SaaS Platform — Final Architecture Snapshot

## 1. Executive Platform Architecture

**Aegivanta** is an enterprise-grade AI-powered Autonomous Cybersecurity & Extended Detection and Response (XDR/SOC) SaaS platform designed for multi-tenant, cloud-native scale.

```
+---------------------------------------------------------------------------------------------------+
|                                      AEGIVANTA CUSTOMER EDGE                                      |
|                                                                                                   |
|  [ Customer Web Portal ]    [ Enterprise SSO / SCIM ]    [ Sensor Fleet: Linux/Win/K8s ]          |
+------------------------------------------+--------------------------------------------------------+
                                           | (TLS 1.3 / Gzip Stream)
                                           v
+---------------------------------------------------------------------------------------------------+
|                                 GLOBAL INGESTION & ACCESS GATEWAY                                 |
|                                                                                                   |
|  - Rate Limiting & Sliding Window Quotas       - Mutual Sensor Token Verification                 |
|  - Multi-Tenant RBAC & Entitlement Gate        - Gzip/Zlib Decompression (Max 10MB Bound)          |
|  - Schema Validation (Flows, Auth, DNS, HTTP)  - Sliding LRU Deduplication (50k event window)     |
+------------------------------------------+--------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------------------+
|                                DISTRIBUTED STREAMING & WORKER PLANE                               |
|                                                                                                   |
|  [ Redis Streams: telemetry:stream ] ---> [ Distributed Workers Pool (K8s HPA Autoscaling) ]      |
|                                           |                                                       |
|                                           +---> [ Real-Time CatBoost / RF ML Inference ]          |
|                                           +---> [ Threat Intelligence Normalization ]             |
|                                           +---> [ Attack Graph & Lateral Movement Engine ]        |
|                                           +---> [ Detection-as-Code Rule Evaluator ]              |
+------------------------------------------+--------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------------------+
|                              DECISION, AI & AUTONOMOUS SOAR PLANE                                 |
|                                                                                                   |
|  - Incident Correlation & Dynamic Risk Scoring (0–100)                                            |
|  - Aegivanta AI Security Copilot (Attack Path Reasoning & Evidence Synthesis)                    |
|  - Autonomous SOAR Remediation (IP Block, Host Isolation, Kill Switches, Approval Gates)          |
|  - Adaptive Feedback Loop (Analyst Ground Truth & Concept Drift Tracking)                         |
+------------------------------------------+--------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------------------+
|                              GOVERNANCE, AUDIT & PERSISTENCE PLANE                                |
|                                                                                                   |
|  [ PostgreSQL (Multi-Tenant Schemas) ]    [ Immutable Tamper-Evident Audit Hash-Chain ]           |
|  [ Compliance Posture Engine (SOC 2, ISO 27001, GDPR, NIST CSF, CIS Controls) ]                  |
|  [ Automated Disaster Recovery & Integrity Verification Engine ]                                  |
+---------------------------------------------------------------------------------------------------+
```
