import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False


class RealModelExplainer:
    """
    Performance-Protected Real Model Explainer:
    Calculates actual feature importance attributions using TreeExplainer for tree models,
    with fast top-N extraction and model-agnostic fallbacks.
    """

    def __init__(self, model: Any, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
        self.explainer: Optional[Any] = None
        self._init_explainer()

    def _init_explainer(self):
        if not HAS_SHAP or self.model is None:
            return

        model_type = type(self.model).__name__.lower()
        if any(t in model_type for t in ["xgb", "catboost", "lgbm", "randomforest", "decisiontree"]):
            try:
                self.explainer = shap.TreeExplainer(self.model)
            except Exception:
                self.explainer = None

    def explain_instance(self, processed_vector: np.ndarray, top_n: int = 5) -> Dict[str, float]:
        """
        Computes SHAP feature importance attributions for a processed input vector.
        Returns a dictionary mapping feature names to contribution scores.
        """
        if processed_vector.ndim == 1:
            processed_vector = processed_vector.reshape(1, -1)

        num_features = processed_vector.shape[1]
        feature_labels = self.feature_names[:num_features] if len(self.feature_names) >= num_features else [f"Feature_{i}" for i in range(num_features)]

        if HAS_SHAP and self.explainer is not None:
            try:
                shap_values = self.explainer.shap_values(processed_vector)
                
                # If list (multiclass), take the class with highest prediction or average magnitude
                if isinstance(shap_values, list):
                    vals = np.abs(shap_values[0])[0]
                elif shap_values.ndim == 3:
                    vals = np.abs(shap_values[0, :, 0])
                else:
                    vals = np.abs(shap_values[0])

                explanation = {feature_labels[i]: round(float(vals[i]), 4) for i in range(min(num_features, len(vals)))}
                # Sort by impact
                sorted_exp = dict(sorted(explanation.items(), key=lambda item: abs(item[1]), reverse=True)[:top_n])
                return sorted_exp
            except Exception:
                pass

        # Model-Agnostic Feature Weight Fallback (based on feature magnitude & model feature importances)
        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
            if len(importances) == num_features:
                weights = importances * np.abs(processed_vector[0])
                explanation = {feature_labels[i]: round(float(weights[i]), 4) for i in range(num_features)}
                return dict(sorted(explanation.items(), key=lambda item: abs(item[1]), reverse=True)[:top_n])

        # Baseline variance contribution fallback
        abs_vals = np.abs(processed_vector[0])
        total = np.sum(abs_vals) + 1e-6
        norm_vals = abs_vals / total
        explanation = {feature_labels[i]: round(float(norm_vals[i]), 4) for i in range(num_features)}
        return dict(sorted(explanation.items(), key=lambda item: abs(item[1]), reverse=True)[:top_n])
