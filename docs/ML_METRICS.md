# SentinelAI Machine Learning Evaluation & Metrics Specification

This document provides the formal mathematical definitions and operational specifications for all performance metrics evaluated within the SentinelAI Intrusion Detection System.

---

## 1. Classification Metrics & Mathematical Formulations

Given a confusion matrix for class $k \in \{1, \dots, K\}$ where:
- $TP_k$: True Positives for class $k$
- $FP_k$: False Positives for class $k$
- $TN_k$: True Negatives for class $k$
- $FN_k$: False Negatives for class $k$

### A. False Positive Rate (FPR)
$$\text{FPR}_k = \frac{FP_k}{FP_k + TN_k}$$

The system-wide macro-averaged False Positive Rate across all $K$ classes is:
$$\text{FPR}_{\text{macro}} = \frac{1}{K} \sum_{k=1}^{K} \frac{FP_k}{FP_k + TN_k}$$

> [!IMPORTANT]
> **Methodological Correction**: In earlier prototype iterations, `fpr = 1 - recall` was used. That formulation represents False Negative Rate ($\text{FNR} = 1 - \text{Recall}$), NOT False Positive Rate. SentinelAI Phase 11 enforces the strict One-vs-Rest formulation $\text{FPR}_k = \frac{FP_k}{FP_k + TN_k}$.

---

### B. Precision (Macro-Averaged)
$$\text{Precision}_k = \frac{TP_k}{TP_k + FP_k}$$

$$\text{Precision}_{\text{macro}} = \frac{1}{K} \sum_{k=1}^{K} \text{Precision}_k$$

---

### C. Recall / Sensitivity (Macro-Averaged)
$$\text{Recall}_k = \frac{TP_k}{TP_k + FN_k}$$

$$\text{Recall}_{\text{macro}} = \frac{1}{K} \sum_{k=1}^{K} \text{Recall}_k$$

---

### D. Macro F1-Score
$$\text{F1}_k = 2 \cdot \frac{\text{Precision}_k \cdot \text{Recall}_k}{\text{Precision}_k + \text{Recall}_k}$$

$$\text{F1}_{\text{macro}} = \frac{1}{K} \sum_{k=1}^{K} \text{F1}_k$$

---

### E. Sample Standard Deviation Across Folds
For $N$-fold Cross-Validation where $S_i$ is the metric score obtained on fold $i \in \{1, \dots, N\}$:

$$\mu = \frac{1}{N} \sum_{i=1}^{N} S_i$$

$$\sigma = \sqrt{\frac{1}{N - 1} \sum_{i=1}^{N} (S_i - \mu)^2}$$

> [!NOTE]
> All standard deviation values (`macro_f1_std`, `precision_std`, `recall_std`, `accuracy_std`) are dynamically calculated across fold observations using sample standard deviation ($ddof=1$). No hardcoded standard deviation values (e.g. `0.001`) are permitted.

---

## 2. Multi-Objective Model Selection Weighting
Model selection uses a multi-objective optimization score:

$$\text{Score} = w_1 \cdot \text{F1}_{\text{macro}} + w_2 \cdot \text{Recall}_{\text{macro}} + w_3 \cdot (1 - \text{FPR}_{\text{macro}}) + w_4 \cdot \text{NormLatency}$$

Where default weights are:
- $w_1 = 0.40$ (Macro F1)
- $w_2 = 0.30$ (Macro Recall)
- $w_3 = 0.20$ (Low FPR Penalty)
- $w_4 = 0.10$ (Inference Latency)
