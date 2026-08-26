# AEGIVANTA — PHASE 20 MODEL DRIFT & QUALITY MONITORING

## 1. Population Stability Index (PSI)
$$PSI = \sum (Actual\% - Expected\%) \times \ln\left(\frac{Actual\%}{Expected\%}\right)$$
- $PSI < 0.10$: **NO_DRIFT** (Stable baseline alignment)
- $0.10 \le PSI < 0.25$: **MODERATE_DRIFT** (Warning: Scheduled retraining recommended)
- $PSI \ge 0.25$: **CRITICAL_DRIFT** (Alert: Severe statistical shift, automatic canary fallback)

## 2. Kolmogorov-Smirnov (KS) & Quality Tracking
Tracks empirical CDF deviations, rolling Precision, Recall, F1, latency ($p_{50}/p_{95}/p_{99}$), and events-per-second throughput.
