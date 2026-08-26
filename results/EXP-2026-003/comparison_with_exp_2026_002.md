# Comparison: EXP-2026-002 (Synthetic Baseline) vs EXP-2026-003 (Real-World NIDS)

**Authoritative Note**: *The metrics from EXP-2026-002 and EXP-2026-003 are NOT directly equivalent or interchangeable. They represent distinct problem formulations, threat surfaces, feature spaces, and traffic origins.*

---

## 1. High-Level Architectural Comparison

| Dimension | EXP-2026-002 | EXP-2026-003 |
| :--- | :--- | :--- |
| **Experiment Purpose** | Deterministic CI & Regression Benchmark | Primary Production-Grade ML Evaluation |
| **Traffic Origin** | Synthetic generator modeling CICIDS2017 | Real physical testbed (105 hardware devices) |
| **Dataset Source** | In-tree `CICIDS2017DataGenerator` | Canadian Institute for Cybersecurity (`CICIoT2023`) |
| **Dataset Hash** | `63a0675954f5e1d97c65eaef49946c7912d0d1481c86201a01f033187fa9751f` | `339dd305a304461aa8e8c17bbdce9f8ea4ec54b608bf315ece6336dbd4d7a778` |
| **Total Record Count** | `5,000` samples | `7,800` samples (26 classes × 300 samples) |
| **Class Topology** | 15 synthetic attack & benign classes | 26 real-world attack & benign classes |
| **Feature Schema** | `schema-v1.0` (30 selected features) | `schema-v2.0` (30 selected flow statistical features) |
| **Raw Feature Engine** | CICIDS2017 78-feature statistical engine | CICIoT2023 39-feature bidirectional flow engine |
| **Data Partitioning** | 80/20 Stratified Split (4k train / 1k test) | 80/20 Stratified Split (6.24k train / 1.56k test) |
| **Cross-Validation** | 5-Fold Stratified CV on Train | 5-Fold Stratified CV on Train |
| **Leakage Isolation**| 100% Split-First Preprocessing | 100% Split-First Preprocessing |

---

## 2. Key Differences in Traffic & Feature Distributions

1. **Hardware-Level Variance**:
   - `EXP-2026-002`: Modeled normal packet distributions parametrically using uniform/normal distributions for CI deterministic guarantees.
   - `EXP-2026-003`: Features authentic hardware jitter, buffer delays, inter-arrival time bursts, and realistic protocol interactions from physical IoT hardware (smart plugs, cameras, gateways, smart bulbs).

2. **Attack Surface & Breadth**:
   - `EXP-2026-002`: Traditional enterprise threats (SSH Brute Force, FTP Patator, DoS Hulk, PortScan).
   - `EXP-2026-003`: Modern IoT & enterprise threats including Mirai GRE floods, Slowloris, ARP/DNS spoofing, web command injection, and dictionary attacks.

3. **Feature Representations**:
   - `EXP-2026-002` focuses heavily on packet length moments and forward/backward header lengths.
   - `EXP-2026-003` incorporates detailed protocol encapsulation flags (HTTP, HTTPS, DNS, Telnet, SMTP, SSH, IRC, TCP, UDP, DHCP, ARP, ICMP, IGMP) alongside rate and variance metrics.

---

## 3. Preservation Policy
- `EXP-2026-002` remains permanently available and immutable for CI pipelines, regression tests, and reproducibility audits.
- `EXP-2026-003` serves as the primary machine learning validation baseline for modern intrusion detection.
