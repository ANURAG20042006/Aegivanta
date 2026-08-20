# Aegivanta — Phase 17: Attack Path Risk Graph Traversal

## 1. Graph Topology Analysis
Multi-hop risk traversal calculates exposure paths across entry points, proxy nodes, identities, and core data stores:
- **Path Likelihood**: Probability of traversal based on asset vulnerability and active alerts.
- **Blast Radius**: Predicted containment disruption.
- **Containment Cut-Points**: Highest leverage containment intercept point.

## 2. API Endpoints
- `GET /api/v1/security/attack-paths`
