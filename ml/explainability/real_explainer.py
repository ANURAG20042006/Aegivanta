import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from backend.app.core.logging import logger

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False


class RealModelExplainer:
    """
    Performance-Protected Real Model Explainer:
    Calculates actual feature importance attributions using SHAP TreeExplainer for tree models,
    with fast top-N extraction. Gracefully returns explanation_available = False on failure without fabricating data.
    """

    def __init__(self, model: Any, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
        self.explainer: Optional[Any] = None
        self._init_explainer()

    def _init_explainer(self):
        if not HAS_SHAP or self.model is None:
            return

        model_obj = getattr(self.model, "model", self.model)
        model_type = type(model_obj).__name__.lower()
        if any(t in model_type for t in ["xgb", "catboost", "lgbm", "randomforest", "decisiontree"]):
            try:
                self.explainer = shap.TreeExplainer(model_obj)
            except Exception as e:
                logger.warning(f"Unable to initialize SHAP TreeExplainer for {model_type}: {e}")
                self.explainer = None

    def explain_instance(
        self,
        processed_vector: np.ndarray,
        model_version: str = "xgboost-v1.0",
        prediction: str = "BENIGN",
        confidence: float = 0.95,
        top_n: int = 5
    ) -> Dict[str, Any]:
        """
        Computes structured SHAP feature attributions for a processed input vector.
        Returns:
          explanation_available: bool
          explanation_method: str
          model_version: str
          prediction: str
          confidence: float
          features: List[Dict[str, Any]] (feature, contribution, direction, rank)
        """
        if processed_vector.ndim == 1:
            processed_vector = processed_vector.reshape(1, -1)

        num_features = processed_vector.shape[1]
        feature_labels = self.feature_names[:num_features] if len(self.feature_names) >= num_features else [f"Feature_{i}" for i in range(num_features)]

        # 1. SHAP TreeExplainer Evaluation
        if HAS_SHAP and self.explainer is not None:
            try:
                shap_values = self.explainer.shap_values(processed_vector)
                
                if isinstance(shap_values, list):
                    vals = shap_values[0][0]
                elif shap_values.ndim == 3:
                    vals = shap_values[0, :, 0]
                else:
                    vals = shap_values[0]

                feature_items = []
                for i in range(min(num_features, len(vals))):
                    contrib = float(vals[i])
                    feature_items.append({
                        "feature": feature_labels[i],
                        "contribution": round(contrib, 4),
                        "direction": "positive" if contrib >= 0 else "negative"
                    })

                # Sort by absolute impact
                feature_items = sorted(feature_items, key=lambda item: abs(item["contribution"]), reverse=True)[:top_n]
                for rank, item in enumerate(feature_items, 1):
                    item["rank"] = rank

                return {
                    "explanation_available": True,
                    "explanation_method": "SHAP TreeExplainer",
                    "model_version": model_version,
                    "prediction": prediction,
                    "confidence": round(confidence, 4),
                    "features": feature_items
                }
            except Exception as e:
                logger.error(f"SHAP explanation failed: {e}")

        # 2. Model Feature Importances Fallback
        model_obj = getattr(self.model, "model", self.model)
        if hasattr(model_obj, "feature_importances_"):
            try:
                importances = model_obj.feature_importances_
                if len(importances) == num_features:
                    weights = importances * processed_vector[0]
                    feature_items = []
                    for i in range(num_features):
                        contrib = float(weights[i])
                        feature_items.append({
                            "feature": feature_labels[i],
                            "contribution": round(contrib, 4),
                            "direction": "positive" if contrib >= 0 else "negative"
                        })

                    feature_items = sorted(feature_items, key=lambda item: abs(item["contribution"]), reverse=True)[:top_n]
                    for rank, item in enumerate(feature_items, 1):
                        item["rank"] = rank

                    return {
                        "explanation_available": True,
                        "explanation_method": "Tree Feature Importances",
                        "model_version": model_version,
                        "prediction": prediction,
                        "confidence": round(confidence, 4),
                        "features": feature_items
                    }
            except Exception as e:
                logger.error(f"Feature importances explanation failed: {e}")

        # Controlled explanation failure (No fake data)
        return {
            "explanation_available": False,
            "explanation_method": None,
            "model_version": model_version,
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "features": []
        }
