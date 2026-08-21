# Aegivanta — Detection Validation Score Engine (Phase 26.3)

## Multi-Metric Scoring Model (0–100)

The Detection Validation Score evaluates empirical detection efficacy across 11 telemetry & ML quality dimensions:

1. **Precision**: Ratio of true positives among total detection events (Target: >= 95%)
2. **Recall**: Detection coverage across active attack vectors (Target: >= 92%)
3. **False Positive Rate (FPR)**: Background noise suppression (Target: <= 4%)
4. **False Negative Rate (FNR)**: Missed threat prevention (Target: <= 8%)
5. **Detection Latency**: Median time to detection (Target: < 25ms)
6. **MITRE ATT&CK Technique Coverage**: Breadth of matrix technique detectors (Target: >= 85%)
7. **Telemetry Coverage**: Completeness of network, endpoint, and cloud signal ingestion
8. **Rule Freshness**: Lifecycle age of declarative AST detection rules
9. **Analyst Feedback Integration**: Ground-truth feedback loop convergence
10. **Purple-Team Simulation Success**: Real-time validation against synthetic ATT&CK probes
11. **Drift Resilience**: Model stability under concept drift
