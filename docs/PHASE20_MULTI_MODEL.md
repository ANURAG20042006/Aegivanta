# AEGIVANTA — PHASE 20 MULTI-MODEL DETECTION SPECIFICATION

## 1. Multi-Tier Model Architecture
1. **Supervised Classifier**: Classical and gradient boosted decision tree classifiers (RandomForest, LightGBM, CatBoost) predicting specific known attack families (DDoS, PortScan, Infiltration, Web Attack).
2. **Anomaly Isolation Detector**: Unsupervised isolation forest detecting extreme distribution deviations.
3. **Behavioral Entity Profiler**: Rolling statistical baselines monitoring host packet volume, flow duration, and protocol entropy.
4. **Calibrated Consensus Arbiter**: Temperature-scaled logit transformation producing calibrated empirical probabilities.
