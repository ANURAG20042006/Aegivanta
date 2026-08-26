# Aegivanta — Phase 17: Detection Coverage Gap Analysis

## 1. ATT&CK Matrix Deficit Profiling
The detection coverage engine correlates active rules and sensor telemetry against the MITRE ATT&CK enterprise matrix to uncover blind spots:
- Highlights unmonitored tactics and techniques.
- Quantifies current detection coverage percentage per technique.
- Delivers actionable telemetry and detection recommendations.

## 2. API Endpoints
- `GET /api/v1/detection/coverage/gaps`
