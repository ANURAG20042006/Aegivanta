# Aegivanta — Phase 17: Dynamic Asset Risk Intelligence

## 1. Multi-Factor 0–100 Asset Risk Scoring
Asset risk scores synthesize 4 weighted dimensions:
1. **Criticality Weight**: Production tiering (CRITICAL / HIGH / MEDIUM / LOW).
2. **Active Alert Density**: Correlated detections within sliding time windows.
3. **Threat Intelligence Exposure**: Known attacker probing.
4. **Lateral Hop Proximity**: Distance to high-value internal infrastructure.

## 2. API Endpoints
- `GET /api/v1/assets/risk`
