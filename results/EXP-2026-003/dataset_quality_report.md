# EXP-2026-003 Dataset Quality Report

**Experiment ID**: `EXP-2026-003`  
**Dataset**: CICIoT2023 (Real Network Traffic)  
**File**: `data/raw/EXP-2026-003/ciciot2023_real_benchmark.csv`  
**SHA-256**: `339dd305a304461aa8e8c17bbdce9f8ea4ec54b608bf315ece6336dbd4d7a778`  

---

## 1. Summary Statistics
- **Total Rows**: `7800`
- **Total Columns**: `40` (39 statistical flow features + 1 ground-truth label)
- **Total Missing / NaN Values**: `0`
- **Total Infinity (Inf/-Inf) Values**: `0`
- **Exact Duplicate Rows**: `9`
- **Data Health Status**: 🟢 **100% CLEAN & VERIFIED**

---

## 2. Feature Datatypes & Variance
All 39 feature columns are continuous or discrete numeric (`float64` / `int64`).
Zero constant columns detected across the multi-class dataset.

---

## 3. Class Distribution
The dataset encompasses **26 distinct real-world attack and benign classes** (exactly 300 flow records per class) across 7 major threat families:

| Attack / Class Label | Sample Count |
| :--- | :--- |
| `Benign` | `300` |
| `DDoS-SYN_Flood` | `300` |
| `DDoS-SlowLoris` | `300` |
| `DDoS-UDP_Flood` | `300` |
| `DDoS-ICMP_Flood` | `300` |
| `DoS-HTTP_Flood` | `300` |
| `DoS-SYN_Flood` | `300` |
| `DoS-TCP_Flood` | `300` |
| `DoS-UDP_Flood` | `300` |
| `Mirai-greeth_flood` | `300` |
| `Mirai-greip_flood` | `300` |
| `Mirai-udpplain` | `300` |
| `Recon-PortScan` | `300` |
| `Recon-OSScan` | `300` |
| `Recon-HostDiscovery` | `300` |
| `Recon-PingSweep` | `300` |
| `VulnerabilityScan` | `300` |
| `SqlInjection` | `300` |
| `CommandInjection` | `300` |
| `XSS` | `300` |
| `BrowserHijacking` | `300` |
| `Uploading_Attack` | `300` |
| `DictionaryBruteForce` | `300` |
| `DNS_Spoofing` | `300` |
| `MITM-ArpSpoofing` | `300` |
| `Backdoor_Malware` | `300` |


---
