# PHASE 37 — USER & ENTITY BEHAVIOR ANALYTICS (UEBA 2.0) SPECIFICATION

## 1. Risk Scoring Formula

$$ URS = \min\left(100, 15 + \text{Egress}_{\text{Multiplier}} + \text{OddHours} \times 20 + \text{VelocityAnomaly} \times 25 + N_{\text{Anomalies}} \times 10 \right) $$

Identities with $URS \ge 80$ are marked `CRITICAL` risk and trigger immediate step-up authentication.
