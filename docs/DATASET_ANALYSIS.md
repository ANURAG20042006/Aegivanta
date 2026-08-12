# SentinelAI Dataset Characteristics & Feature Analysis Document

**Experiment Reference**: `EXP-2026-002`  
**Dataset Identifier**: `synthetic_cicids2017_benchmark`  
**Dataset Specification**: High-fidelity synthetic benchmark matching Canadian Institute for Cybersecurity (CICIDS2017) feature schema.

---

## 1. Dataset Overview & Sample Statistics
- **Total Dataset Size**: 1,500 continuous flow vectors
- **Total Features**: 78 raw input continuous and discrete network features
- **Target Target Classes**: 18 distinct network traffic categories (1 BENIGN + 17 cyber attack classes)
- **Train / Test Split Ratio**: 80% Train (1,200 samples) / 20% Test (300 samples)
- **Missing / Infinite Values**: Cleaned via `CICIDS2017Preprocessor.clean_dataset()` using median imputation and finite clipping.

---

## 2. Target Class Distribution Table

| Class Index | Class Name | Category | Sample Count | Percentage (%) | Train Split (80%) | Test Split (20%) |
|-------------|------------|----------|--------------|----------------|-------------------|------------------|
| 0 | **BENIGN** | Normal Traffic | 1,050 | 70.0% | 840 | 210 |
| 1 | **DoS Hulk** | Denial of Service | 27 | 1.80% | 22 | 5 |
| 2 | **Port Scan** | Reconnaissance | 26 | 1.73% | 21 | 5 |
| 3 | **DDoS** | Distributed DoS | 26 | 1.73% | 21 | 5 |
| 4 | **DoS Slowloris** | Denial of Service | 25 | 1.67% | 20 | 5 |
| 5 | **DoS GoldenEye** | Denial of Service | 25 | 1.67% | 20 | 5 |
| 6 | **FTP-Patator** | Brute Force | 25 | 1.67% | 20 | 5 |
| 7 | **SSH-Patator** | Brute Force | 25 | 1.67% | 20 | 5 |
| 8 | **Botnet** | Botnet C2 | 24 | 1.60% | 19 | 5 |
| 9 | **Web Attack - XSS** | Web Vulnerability | 24 | 1.60% | 19 | 5 |
| 10 | **Web Attack - SQL Injection** | Web Vulnerability | 24 | 1.60% | 19 | 5 |
| 11 | **Web Attack - Brute Force** | Web Vulnerability | 24 | 1.60% | 19 | 5 |
| 12 | **Infiltration** | Advanced Threat | 23 | 1.53% | 18 | 5 |
| 13 | **Heartbleed** | Exploit | 23 | 1.53% | 18 | 5 |
| 14 | **Malware** | Host Threat | 23 | 1.53% | 18 | 5 |
| 15 | **Ransomware** | Host Threat | 22 | 1.47% | 17 | 5 |
| 16 | **Zero-Day Anomaly** | Novel Threat | 22 | 1.47% | 17 | 5 |
| 17 | **Data Exfiltration** | Data Loss | 22 | 1.47% | 17 | 5 |

---

## 3. Feature Selection & Scale Characteristics
Top 30 features selected via `SelectKBest(f_classif)` include:
1. `Destination Port`
2. `Flow Duration`
3. `Total Fwd Packets`
4. `Total Length of Fwd Packets`
5. `Fwd Packet Length Max`
6. `Flow Bytes/s`
7. `Flow Packets/s`
8. `Flow IAT Mean`
9. `Fwd PSH Flags`
10. `Bwd Header Length`
