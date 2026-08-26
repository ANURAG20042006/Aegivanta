# Phase 48: Enterprise AI/ML Model Registry V2

## Overview
The Model Registry V2 serves as the single source of truth for all ML artifacts in AEGIVANTA.

## Supported Model Families
1. **CatBoost (`CATBOOST`)**: Primary tabular threat classifier for network flow telemetry. P99 latency < 3.5ms.
2. **XGBoost (`XGBOOST`)**: High-speed anomaly detector for host and endpoint process telemetry.
3. **PyTorch GNN (`PYTORCH_GNN`)**: Graph Neural Network for detecting multi-hop lateral movement across Active Directory topologies.
4. **Transformer (`TRANSFORMER`)**: NLP embedding engine for phishing detection and command line obfuscation decoding.
5. **Isolation Forest (`ISOLATION_FOREST`)**: Unsupervised baseline model for insider data exfiltration.

## Champion-Challenger Workflow
- Continuous evaluation against production validation datasets.
- Automatic promotion when challenger model exceeds champion accuracy and latency thresholds.
