# Model Calibration & Confidence Audit Report

**Experiment**: `EXP-2026-003-B1`  
**Evaluated Model**: LightGBM Champion  
**Test Partition**: 1,560 untouched samples  

---

## 1. Summary Calibration Metrics

- **Average Confidence on Correct Predictions**: **`0.8988`** (High confidence)
- **Average Confidence on Incorrect Predictions**: **`0.4244`** (Moderate overconfidence)
- **Total Misclassified Samples**: `500`
- **High-Confidence Errors (Probability > 0.85)**: **`23`** (4.6% of all errors)

---

## 2. High-Confidence Error Analysis in Security Operations

High-confidence errors occur predominantly when:
1. An attack vector mimics another protocol flood exactly (e.g. `Mirai-greeth_flood` misclassified as `Mirai-greip_flood` with >90% probability).
2. A single-packet scan probe matches standard benign UDP DNS query profiles with high certainty.
