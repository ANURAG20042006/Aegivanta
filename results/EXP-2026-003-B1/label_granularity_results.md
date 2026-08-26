# Label Granularity Sensitivity Analysis

**Experiment**: `EXP-2026-003-B1`  
**Dataset**: CICIoT2023-derived Aegivanta benchmark subset  
**Model Architecture**: LightGBM (`schema-v2.0`)  
**Evaluation Protocol**: Frozen Untouched Test Partition (1,560 samples)  

---

## 1. Empirical Granularity Comparison Table

| Classification Task | Class Count | Macro F1 | Macro Precision | Macro Recall | Accuracy | Weighted F1 | Operational Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Task 1: Granular NIDS** | 26 | **`0.6800`** | `0.6844` | `0.6795` | `0.6795` | `0.6800` | Detailed threat attribution & playbook selection |
| **Task 2: Attack Family** | 7 | **`0.8121`** | `0.8202` | `0.8100` | `0.7936` | `0.7950` | Threat family alert routing |
| **Task 3: Binary Detection** | 2 | **`0.8998`** | `0.9213` | `0.8807` | `0.9859` | `0.9855` | Perimeter firewall threat filtering |

---

## 2. Granularity Sensitivity Interpretation

1. **Dramatic Macro F1 Gain Under Coarser Abstractions**:
   - Collapsing sub-variants into **7 Attack Families** increases Macro F1 from `0.6800` to **`0.8121`** (+0.1321 absolute gain).
   - Evaluating **Binary Detection (Benign vs Malicious)** achieves **`0.8998`** Macro F1 and **`98.59%`** Accuracy.
2. **Scientific Conclusion**:
   - The `0.6800` baseline in Task 1 is heavily driven by intra-family sub-variant confusion rather than complete failure to detect attacks.
   - The model reliably detects that network traffic is malicious, but struggles to discriminate between identical-protocol flood sub-variants without L7 inspection.
