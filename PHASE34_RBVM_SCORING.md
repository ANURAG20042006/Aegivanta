# PHASE 34 — RBVM COMPOSITE SCORING FORMULA SPECIFICATION

## 1. Mathematical Formulation

$$ RBVM\_Score = \min\left(100, \left[ 0.35 \cdot (CVSS \cdot 10) + 0.35 \cdot (EPSS \cdot 100) + 0.20 \cdot KEV + 0.10 \cdot Ransomware \right] \cdot Multiplier_{Tier} \right) $$

Where:
- $CVSS$: CVSS v3.1 Base Score (0.0 to 10.0)
- $EPSS$: EPSS 2.0 Exploit Probability (0.000 to 1.000)
- $KEV$: 100.0 if listed in CISA KEV catalog, else 0.0
- $Ransomware$: 100.0 if associated with active ransomware cartels, else 0.0
- $Multiplier_{Tier}$: 1.15 for Tier 1 Critical Assets, 1.00 for Tier 2, 0.85 for Tier 3
