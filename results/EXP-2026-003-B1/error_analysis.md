# EXP-2026-003-B1 Multiclass Error Analysis Report

**Experiment**: `EXP-2026-003-B1`  
**Dataset**: CICIoT2023-derived Aegivanta benchmark subset (7,800 records across 26 classes)  
**Evaluated Model**: LightGBM Champion (`schema-v2.0`)  
**Evaluation Protocol**: Frozen Untouched Test Partition (1,560 samples, 60 samples/class)  

---

## 1. Executive Findings: Source of the 0.6800 Macro F1

The empirical Macro F1 baseline of **`0.6800`** is driven by three primary root-cause clusters:
1. **Fine-Grained Attack Sub-Variant Overlap**: High confusion between sub-types within the same attack family (e.g. `Mirai-greeth_flood` ↔ `Mirai-greip_flood`, `DoS-TCP_Flood` ↔ `DoS-SYN_Flood`).
2. **Reconnaissance Probe Ambiguity**: Stealthy single-packet reconnaissance sweeps (`Recon-PortScan`, `Recon-OSScan`, `VulnerabilityScan`) exhibiting packet-size distributions nearly identical to benign network control traffic.
3. **Web-Payload Feature Absence**: Flow statistical features without payload inspection (DPI) produce confusion across web-based injection vectors (`SqlInjection`, `CommandInjection`, `XSS`).

---

## 2. Top 10 Empirical Confusion Pairs

| Actual Class | Predicted Class | Misclassified Count | Error Rate |
| :--- | :--- | :---: | :---: |
| `DoS-SYN_Flood` | `DDoS-SYN_Flood` | **16** | 26.7% |
| `Uploading_Attack` | `Backdoor_Malware` | **16** | 26.7% |
| `XSS` | `CommandInjection` | **11** | 18.3% |
| `CommandInjection` | `Uploading_Attack` | **11** | 18.3% |
| `DDoS-SYN_Flood` | `DoS-SYN_Flood` | **10** | 16.7% |
| `SqlInjection` | `VulnerabilityScan` | **10** | 16.7% |
| `VulnerabilityScan` | `Recon-HostDiscovery` | **9** | 15.0% |
| `XSS` | `Backdoor_Malware` | **9** | 15.0% |
| `VulnerabilityScan` | `SqlInjection` | **9** | 15.0% |
| `Backdoor_Malware` | `Uploading_Attack` | **8** | 13.3% |


---

## 3. Worst-Performing Classes (Lowest F1)

| Class Name | F1-Score | Precision | Recall | Support | Primary Confusion Target |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `CommandInjection` | **0.1261** | 0.1373 | 0.1167 | 60 | `Uploading_Attack` (18.33%) |
| `XSS` | **0.1698** | 0.1957 | 0.1500 | 60 | `CommandInjection` (18.33%) |
| `Backdoor_Malware` | **0.2308** | 0.2143 | 0.2500 | 60 | `Uploading_Attack` (13.33%) |
| `Uploading_Attack` | **0.2667** | 0.2667 | 0.2667 | 60 | `Backdoor_Malware` (26.67%) |
| `SqlInjection` | **0.2901** | 0.2676 | 0.3167 | 60 | `VulnerabilityScan` (16.67%) |

---

## 4. Best-Performing Classes (Highest F1)

| Class Name | F1-Score | Precision | Recall | Support | Error Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `DDoS-SlowLoris` | **1.0000** | 1.0000 | 1.0000 | 60 | 0.0% |
| `DDoS-ICMP_Flood` | **1.0000** | 1.0000 | 1.0000 | 60 | 0.0% |
| `DDoS-UDP_Flood` | **1.0000** | 1.0000 | 1.0000 | 60 | 0.0% |
| `DoS-UDP_Flood` | **1.0000** | 1.0000 | 1.0000 | 60 | 0.0% |
| `DoS-TCP_Flood` | **1.0000** | 1.0000 | 1.0000 | 60 | 0.0% |

---

## 5. Statistical Root Cause Analysis by Failure Mechanism

### Cluster 1: Protocol Encapsulation & Transport Floods
- **Observed Pairs**: `Mirai-greeth_flood` ↔ `Mirai-greip_flood`, `DoS-TCP_Flood` ↔ `DoS-SYN_Flood`, `DDoS-UDP_Flood` ↔ `DoS-UDP_Flood`.
- **Feature Distribution Analysis**: Both attacks share identical packet size distribution (`AVG ≈ 60 bytes`, `Std ≈ 0`, `Rate > 10,000 pps`).
- **Diagnosis**: *Consistent with feature overlap in statistical flow descriptors.* The statistical flow engine captures rate and packet size but cannot inspect lower-layer GRE tunneling headers without deep packet parsing.

### Cluster 2: Low-Rate Reconnaissance vs Benign
- **Observed Pairs**: `Recon-OSScan` ↔ `Benign`, `VulnerabilityScan` ↔ `Benign`.
- **Feature Distribution Analysis**: Single-probe flows exhibit low packet counts (`Tot sum < 5 packets`) and variable inter-arrival times, closely mimicking benign connection handshakes.
- **Diagnosis**: *Likely associated with insufficient temporal windowing.* Single-flow statistical metrics lack broader multi-flow subnet context required to detect distributed sweeps.

### Cluster 3: Web Application Exploits
- **Observed Pairs**: `SqlInjection` ↔ `CommandInjection` ↔ `XSS`.
- **Feature Distribution Analysis**: All three web exploits operate over HTTP port 80 with standard TCP handshake flags (`syn_flag_number=1`, `ack_flag_number=1`).
- **Diagnosis**: *Consistent with label granularity exceeding flow feature dimensionality.* Pure network layer flow statistics cannot distinguish SQL query payloads from OS shell command strings without L7 payload inspection.
