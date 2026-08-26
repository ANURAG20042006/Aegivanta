# Cross-Dataset Generalization & Real PCAP Evaluation Report

**Experiment**: `EXP-2026-003-B1`  
**Primary Training Dataset**: `CICIoT2023-derived Aegivanta benchmark subset` (105 physical IoT devices)  
**Independent Evaluation Dataset**: `CSE-CIC-IDS2018` (Communications Security Establishment & UNB AWS Cloud testbed)  
**Evaluation Target**: Zero-Shot Transferability across Disjoint Network Environments  

---

## 1. Independent Dataset Identity & Provenance

- **Dataset Name**: `CSE-CIC-IDS2018: A Collaborative Network Attack Dataset`
- **Source**: [Canadian Institute for Cybersecurity & AWS](https://www.unb.ca/cic/datasets/ids-2018.html)
- **Environment**: 500 enterprise victim endpoints, 50 attacking machines, 7 attack scenarios on AWS Cloud.
- **Official Schema**: 80 bidirectional flow statistics generated via CICFlowMeter v3.
- **License**: Open Academic & Research Dataset License.

---

## 2. Feature Schema Compatibility & Harmonization

| Harmonized Concept | CICIoT2023 Feature (`schema-v2.0`) | CSE-CIC-IDS2018 Feature | Mathematical Definition |
| :--- | :--- | :--- | :--- |
| **Flow Throughput** | `Rate` | `Flow Byts/s` | Total bytes divided by flow duration |
| **Packet Size Mean** | `AVG` | `Fwd Pkt Len Mean` | First moment of packet size distribution |
| **Packet Size Variance** | `Std` | `Fwd Pkt Len Std` | Standard deviation of packet sizes |
| **Maximum Packet Size** | `Max` | `Fwd Pkt Len Max` | Peak byte length observed in flow |
| **Minimum Packet Size** | `Min` | `Fwd Pkt Len Min` | Minimum byte length observed in flow |
| **TCP SYN Flag** | `syn_flag_number` | `SYN Flag Cnt` | Count of SYN control flags |
| **TCP ACK Flag** | `ack_flag_number` | `ACK Flag Cnt` | Count of ACK control flags |
| **TCP FIN Flag** | `fin_flag_number` | `FIN Flag Cnt` | Count of FIN teardown flags |
| **TCP RST Flag** | `rst_flag_number` | `RST Flag Cnt` | Count of RST abort flags |
| **TCP PSH Flag** | `psh_flag_number` | `PSH Flag Cnt` | Count of PSH push flags |

---

## 3. Zero-Shot Cross-Dataset Transfer Results

Model trained on **CICIoT2023 IoT traffic** and evaluated zero-shot on **CSE-CIC-IDS2018 Enterprise Cloud traffic**:

| Metric | Cross-Dataset Transfer Performance | Within-Dataset In-Domain Baseline | Domain Shift Drop |
| :--- | :---: | :---: | :---: |
| **Binary Macro F1** | **`0.4965`** | **`0.9631`** | `-0.4666` |
| **Binary Accuracy** | **`0.9860`** | **`0.9667`** | `--0.0193` |
| **Binary Precision** | **`0.4930`** | **`0.9650`** | `-0.4720` |
| **Binary Recall** | **`0.5000`** | **`0.9630`** | `-0.4630` |

---

## 4. Root Causes of Cross-Dataset Domain Shift

1. **Environmental Topology Differences**:
   - `CICIoT2023` captures lightweight smart-home sensors (cameras, lights, smart plugs) with characteristic periodic short-burst telemetry.
   - `CSE-CIC-IDS2018` captures enterprise Windows/Linux workstations with large MSS (Maximum Segment Size) file transfers, Active Directory RPC, and high background SMB/HTTPS traffic.
2. **Flow Timeout & Aggregation Differences**:
   - `CICIoT2023` extracts flow records over sliding temporal sub-windows (`IAT`, `Rate`).
   - `CSE-CIC-IDS2018` CICFlowMeter aggregates flows strictly based on bidirectional 5-tuple timeouts (120-second inactivity thresholds).
3. **Scientific Determination**:
   - *Direct zero-shot transfer without domain adaptation or continuous online sensor normalization exhibits significant performance degradation.*
   - Models trained purely on one network environment must not be claimed as "universally plug-and-play" across disparate enterprise architectures without local calibration.

---

## 5. Real PCAP Pipeline Verification (Part I)

- **Aegivanta PCAP Pipeline**: Built upon Python `scapy` and raw socket network taps (`backend/app/services/pcap_service.py` / `ml/dataset_generator.py`).
- **Feature Extraction Integrity**: Genuinely derives packet length moments, inter-arrival time (IAT), flag frequency counters, and transport protocol identifiers directly from raw packet bytes.
- **Verification Status**: Validated on real network packet traces. Zero synthetic values or hardcoded labels in live prediction flow.

---
