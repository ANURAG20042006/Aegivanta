# EXPLAINABLE AI (XAI) ARCHITECTURE & SPECIFICATION

**System Component**: SentinelAI Real Model Explainer (`ml/explainability/real_explainer.py`)  
**Specification Version**: 1.0  

---

## 1. Overview & Research Integrity

SentinelAI enforces strict explainability integrity. Feature attributions must come exclusively from true model explainers or feature importances calculated on actual input flow attributes. **Synthetic, random, or hardcoded SHAP values are strictly prohibited.**

If a model architecture is unsupported for Tree SHAP or linear attributions, the explainer returns an explicit failure payload (`available: false`, `reason: "Model architecture ... is unsupported"`). It never fabricates explanations for visual completeness.

---

## 2. Explanation Contract Payload

Every explanation request yields a standardized contract payload:

```json
{
  "available": true,
  "reason": null,
  "explainer_type": "SHAP TreeExplainer",
  "model_version": "random_forest_v1.0",
  "prediction": "DoS Hulk",
  "confidence": 0.9421,
  "timestamp": "2026-08-13T10:45:00.000Z",
  "xai_latency_ms": 4.12,
  "top_features": [
    {
      "feature": "flow_packets_s",
      "input_value": 1500.0,
      "contribution": 0.4215,
      "rank": 1,
      "direction": "POSITIVE"
    },
    {
      "feature": "packet_length_std",
      "input_value": 24.5,
      "contribution": -0.1820,
      "rank": 2,
      "direction": "NEGATIVE"
    }
  ]
}
```

### Contract Attributes:
- `available` (*boolean*): Indicates whether a legitimate model explanation was computed.
- `reason` (*string | null*): Descriptive explanation if `available == false`.
- `explainer_type` (*string*): Algorithm used (`SHAP TreeExplainer`, `Tree Feature Importances`, or `UnsupportedModel`).
- `model_version` (*string*): Identifier of the active model evaluated.
- `xai_latency_ms` (*float*): Microsecond/millisecond execution time taken to compute attributions.
- `top_features` (*array*): Top-N ranked features with directional contribution (`POSITIVE` or `NEGATIVE`).

---

## 3. Supported Model Architecture Matrix

| Model Family | Explainer Algorithm | Handling on Unsupported |
| :--- | :--- | :--- |
| Random Forest | SHAP TreeExplainer / Importances | N/A (Fully Supported) |
| XGBoost / LightGBM / CatBoost | SHAP TreeExplainer / Importances | N/A (Fully Supported) |
| Decision Trees | SHAP TreeExplainer / Importances | N/A (Fully Supported) |
| Non-Tree / Deep Learning / Linear | N/A | Returns `available: false` with reason |

---

## 4. Performance & Latency Controls

To ensure high-throughput network flow inspection:
1. **Top-N Extraction**: Only top N (default `5`) features by absolute contribution are returned.
2. **Timing Measurement**: Execution time is measured per instance (`xai_latency_ms`).
3. **Fail-Safe**: If tree explainer fails during calculation, the system falls back to tree feature importances or returns `available: false` without throwing HTTP 500 errors.
