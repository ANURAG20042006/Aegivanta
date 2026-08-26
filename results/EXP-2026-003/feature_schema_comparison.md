# Feature Schema Comparison: EXP-2026-002 (v1.0) vs EXP-2026-003 (v2.0)

**Old Schema**: `schema-v1.0` (CICIDS2017 Synthetic 30 selected features)  
**New Schema**: `schema-v2.0` (CICIoT2023 Real 39 bidirectional flow features)  

---

## 1. Structural Comparison

| Feature Category | `schema-v1.0` (EXP-2026-002) | `schema-v2.0` (EXP-2026-003) | Match Classification |
| :--- | :--- | :--- | :--- |
| **Header Metrics** | `Fwd Header Length`, `Bwd Header Length` | `Header_Length` | **SEMANTIC MATCH** |
| **Packet Rates** | `Flow Packets/s`, `Flow Bytes/s` | `Rate`, `Srate`, `Drate` | **SEMANTIC MATCH** |
| **TCP Flags** | `SYN Flag Count`, `RST Flag Count`, `PSH Flag Count`, `ACK Flag Count`, `URG Flag Count` | `syn_flag_number`, `rst_flag_number`, `psh_flag_number`, `ack_flag_number`, `fin_flag_number`, `ece_flag_number`, `cwr_flag_number` | **EXACT MATCH** |
| **Packet Sizes** | `Packet Length Mean`, `Packet Length Std`, `Min Packet Length`, `Max Packet Length`, `Average Packet Size` | `AVG`, `Std`, `Min`, `Max`, `Tot sum`, `Tot size`, `Variance` | **EXACT MATCH** |
| **Inter-Arrival Time**| `Flow IAT Mean`, `Flow IAT Std` | `IAT` | **SEMANTIC MATCH** |
| **Protocol Encapsulation**| Not explicitly multi-flagged | `HTTP`, `HTTPS`, `DNS`, `Telnet`, `SMTP`, `SSH`, `IRC`, `TCP`, `UDP`, `DHCP`, `ARP`, `ICMP`, `IGMP`, `IPv`, `LLC` | **NEW FEATURE** |
| **Network Metadata** | `Destination Port`, `Flow Duration` | `Time_To_Live`, `Protocol Type` | **DERIVABLE / SAFE** |

---

## 2. Policy on Schema Compatibility
Aegivanta preserves both schema versions independently:
- `schema-v1.0` is permanently mapped to `EXP-2026-002`.
- `schema-v2.0` is permanently mapped to `EXP-2026-003`.
Neither schema overwrites or invalidates the other.
