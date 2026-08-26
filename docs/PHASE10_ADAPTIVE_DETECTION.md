# Aegivanta — Phase 10: Adaptive Detection Intelligence & Model Lifecycle

## 1. Ground-Truth Analyst Feedback Loop
Security analysts tag incident detections during triage:
- `TRUE_POSITIVE`: Confirmed security threat.
- `FALSE_POSITIVE`: Benign anomalous pattern.
- `BENIGN`: Verified legitimate administrative activity.
- `UNKNOWN`: Insufficient evidence for determination.

Feedback is persisted in `detection_feedback` and accumulated into retraining dataset partitions.

## 2. Concept Drift & Feature Drift Monitoring
- **Accumulated Window Drift Detector**: Evaluates sliding windows of analyst verdicts.
- **Drift Score**: `drift_score = 1.0 - (True Positives / Total Feedback)`. If drift exceeds `0.25`, an automated retraining alert is triggered.

## 3. Champion / Challenger Model Promotion
- **Candidate Validation**: Challenger models must pass validation thresholds:
  - Validation accuracy >= Champion
  - False positive rate <= 2.5%
  - Latency P95 <= 15ms
- **Safe Promotion**: The promotion workflow atomically updates model states (`ACTIVE`, `PREVIOUS_CHAMPION`) with immediate rollback capability.
