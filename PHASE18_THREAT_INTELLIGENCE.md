# AEGIVANTA — PHASE 18 THREAT INTELLIGENCE SPECIFICATION

## 1. IOC Lifecycle & Scoring Model
Indicators of Compromise (IOCs) transition through standardized states:
- `ACTIVE`: Currently identified as malicious and triggering alerts.
- `EXPIRED`: Confidence decayed past threshold or explicit expiration reached.
- `ARCHIVED`: Retained for historical correlation.
- `REVOKED`: False positive identified and removed from active blocking.

## 2. Threat Score Calculation Formula
The 0–100 Threat Score is dynamically calculated as:
$$\text{Score} = (\text{SourceReliability} + \text{Confidence} + \text{Sightings} + \text{Severity} + \text{Campaign} + \text{Actor}) \times \text{DecayFactor}$$

- **Source Reliability** (0–20 pts)
- **Base Confidence** (0–25 pts)
- **Sightings Weight** (0–20 pts)
- **Severity Rating** (0–15 pts)
- **Campaign Association** (10 pts)
- **Threat Actor Attribution** (10 pts)
- **Decay Factor**: Decays 10% per 30 days of inactivity ($1.0 - \frac{\text{days}}{300}$, floor 0.5).
