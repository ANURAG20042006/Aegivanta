# PHASE 36 — MICROSEGMENTATION, SOFTWARE-DEFINED PERIMETER (SDP) & ZTNA 2.0 ARCHITECTURE

## 1. Executive Summary

Phase 36 delivers an enterprise Microsegmentation, Software-Defined Perimeter (SDP), and Zero Trust Network Access (ZTNA 2.0) platform:
1. **Identity-Bound Encrypted Overlays**: WireGuard/IPsec mTLS tunnels established between endpoints and SDP connectors.
2. **Layer 4 & Layer 7 Microsegmentation**: Kernel eBPF isolation rules restricting east-west workload communication across VPC and container mesh boundaries.
3. **Continuous Device Trust Attestation**: Real-time evaluation of device health, security posture, and velocity before granting segment access.
4. **Lateral Movement Interception**: Automated blocking and isolation of unauthorized inter-segment reconnaissance and pivoting attempts.
5. **Dynamic Network Mesh Visualizer**: Topologically mapped security enclaves and active flow trajectories.

## 2. Microsegmentation System Architecture

```
+-----------------------------------------------------------------------------------+
|               AEGIVANTA SOFTWARE-DEFINED PERIMETER & ZTNA 2.0 NEXUS               |
|                                                                                   |
|  [Authenticated Client / Workload Identity]                                       |
|        |                                                                          |
|        v (Mutual-TLS WireGuard Overlay Tunnel)                                    |
|  +-----------------------------------------------------------------------------+  |
|  |                     SDP / ZTNA CONNECTOR GATEWAY FLEET                      |  |
|  |  - us-east-1, eu-west-1, ap-southeast-1 Dynamic Edge Nodes                    |  |
|  |  - Continuous Device Certificate & Trust Score Evaluator (0–100)            |  |
|  +------------------------------------+----------------------------------------+  |
|                                       |                                           |
|            +--------------------------+--------------------------+                |
|            |                                                     |                |
|            v                                                     v                |
|  +-----------------------------------+     +-----------------------------------+  |
|  |     L4/L7 POLICY ENGINE (eBPF)    |     |  LATERAL MOVEMENT DEFENSE ENGINE  |  |
|  |  - Source/Dest Segment Isolation  |     |  - East-West Port Sweep Detection |  |
|  |  - Protocol/Port Whitelisting     |     |  - Automated Boundary Isolation   |  |
|  |  - Min Trust Score Gating         |     |  - Instant Workload Quarantine    |  |
|  +-----------------+-----------------+     +-----------------+-----------------+  |
|                    |                                         |                    |
|                    +--------------------+--------------------+                    |
|                                         |                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  |                  DYNAMIC NETWORK FLOW & TOPOLOGY MESH GRAPH                 |  |
|  |  - DMZ / Application Mesh / Payment VPC / Core Database / HSM Key Vault     |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```
