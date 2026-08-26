# EXP-2026-003 Leakage Audit Report

**Audit Target**: `ciciot2023_real_benchmark.csv`  
**Dataset**: CICIoT2023  
**Auditor**: Production Security & ML Auditor  

---

## 1. Leakage Analysis by Risk Category

| Risk Category | Feature Examined | Audit Finding | Status |
| :--- | :--- | :--- | :--- |
| **IP Addresses** | `src_ip`, `dst_ip` | Completely absent from flow feature vector by design in CICIoT2023 | 🟢 **ZERO LEAKAGE** |
| **MAC Addresses** | `src_mac`, `dst_mac` | Completely excluded from tabular flow features | 🟢 **ZERO LEAKAGE** |
| **Port Identifiers** | `src_port`, `dst_port`| Excluded from 39 flow statistical features | 🟢 **ZERO LEAKAGE** |
| **Timestamps / Clocks** | Absolute Epoch Time | Excluded; only relative flow `Duration`, `IAT` (Inter-Arrival Time) retained | 🟢 **ZERO LEAKAGE** |
| **Attack Scenario IDs** | `scenario_id` | Excluded; label is pure ground-truth target | 🟢 **ZERO LEAKAGE** |
| **Generated Identifiers**| `flow_id` | Excluded | 🟢 **ZERO LEAKAGE** |

---

## 2. Partition Isolation Guarantee
All transformations (scaling, imputation, feature selection, and class balancing) are strictly fitted on the **Training partition only**. Validation and Test partitions are transformed using parameters frozen from training.

---
