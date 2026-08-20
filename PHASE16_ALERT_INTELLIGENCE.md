# Aegivanta — Phase 16: Alert Intelligence, Deduplication & Prioritization

## 1. Alert Fingerprinting & Deduplication
- **Fingerprint Hash**: SHA-256 computation over `(source_ip, destination_ip, attack_type, signature)`.
- **Temporal Grouping**: Alerts within sliding timeframes are clustered into `AlertGroup` entities linked to parent incidents.
- **Forensic Preservation**: All raw alert records remain permanently queryable for legal/forensic chain-of-custody.

## 2. Explainable 0–100 Priority Scoring
Alert prioritization normalizes 6 distinct risk dimensions into a 0–100 score:
1. **Severity Base** (0–30 pts)
2. **Asset Criticality** (0–25 pts)
3. **Threat Intelligence Reputation** (0–15 pts)
4. **Attack Vector Risk & Lateral Movement** (0–15 pts)
5. **Detection Confidence** (0–10 pts)
6. **Historical Behavioral Anomaly** (0–5 pts)

## 3. Endpoints
- `GET /api/v1/alerts/{id}/priority`
- `GET /api/v1/alerts/groups/active`
