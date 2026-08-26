# Feature Discriminative & Redundancy Analysis

**Experiment**: `EXP-2026-003-B1`  
**Dataset**: CICIoT2023-derived Aegivanta benchmark subset  

---

## 1. Top Discriminative Features (LightGBM Split Gain)

| Rank | Feature Name | Split Importance | Importance Share |
| :---: | :--- | :---: | :---: |
| 1 | `Rate` | 7843 | 11.0% |
| 2 | `IAT` | 7741 | 10.86% |
| 3 | `Time_To_Live` | 5866 | 8.23% |
| 4 | `Tot sum` | 5690 | 7.98% |
| 5 | `Max` | 5500 | 7.72% |
| 6 | `Header_Length` | 5246 | 7.36% |
| 7 | `Std` | 3877 | 5.44% |
| 8 | `AVG` | 3167 | 4.44% |
| 9 | `HTTPS` | 3163 | 4.44% |
| 10 | `UDP` | 3148 | 4.42% |

---

## 2. High Collinearity & Feature Redundancy Clusters

The following feature pairs exhibit Pearson correlation $r > 0.80$:

| Feature A | Feature B | Correlation ($r$) | Redundancy Classification |
| :--- | :--- | :---: | :--- |
| `ARP` | `IPv` | **1.0** | `COLLINEAR_REDUNDANT` |
| `AVG` | `Tot size` | **1.0** | `COLLINEAR_REDUNDANT` |
| `IPv` | `LLC` | **1.0** | `COLLINEAR_REDUNDANT` |
| `ARP` | `LLC` | **1.0** | `COLLINEAR_REDUNDANT` |
| `syn_flag_number` | `syn_count` | **0.9473** | `COLLINEAR_REDUNDANT` |
| `Max` | `Std` | **0.8989** | `MODERATE_CORRELATION` |
| `Header_Length` | `TCP` | **0.8951** | `MODERATE_CORRELATION` |
| `rst_flag_number` | `rst_count` | **0.8638** | `MODERATE_CORRELATION` |

---

## 3. Findings on Feature Behavior
- **Highest Predictive Power**: Packet size moments (`AVG`, `Std`, `Min`, `Max`) and flow rates (`Rate`, `IAT`) account for over 65% of total tree splits.
- **Redundancy Clusters**: `Tot sum` and `Tot size` are highly collinear ($r > 0.95$), indicating that one can be pruned without loss of representational capacity.
