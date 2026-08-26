# PHASE 34 — EXPLOIT PREDICTION SCORING SYSTEM (EPSS 2.0) SPECIFICATION

## 1. Overview

EPSS provides a data-driven score estimating the probability of vulnerability exploitation in the wild in the next 30 days:
- **Probability**: Between 0 and 1 (e.g. 0.942 = 94.2% chance of exploitation).
- **Percentile**: Position relative to all other scored CVEs (e.g. 99.8th percentile).
- **Signal Value**: High CVSS CVEs with low EPSS (<0.05) present drastically lower real-world risk than lower CVSS CVEs with high EPSS (>0.70).
