import time
import numpy as np
from datetime import datetime, timezone
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
    with fast top-N extraction and strict execution latency timing.
    Returns structured explanation contract without fabricating data.
    """

    def __init__(self, model: Any, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
        self.explainer: Optional[Any] = None
        self.explainer_type: str = "NotAvailable"
        self._init_explainer()

    def _init_explainer(self):
        if self.model is None:
            self.explainer_type = "NotAvailable"
            return

        model_obj = getattr(self.model, "model", self.model)
        model_type = type(model_obj).__name__.lower()

        if "catboost" in model_type:
            self.explainer_type = "SHAP TreeExplainer"
            self.explainer = "catboost_native"
        elif any(t in model_type for t in ["xgb", "lgbm", "randomforest", "decisiontree", "tree"]):
            if HAS_SHAP:
                try:
                    self.explainer = shap.TreeExplainer(model_obj)
                    self.explainer_type = "SHAP TreeExplainer"
                except Exception as e:
                    logger.warning(f"Unable to initialize SHAP TreeExplainer for {model_type}: {e}")
                    self.explainer = None
                    self.explainer_type = "Tree Feature Importances"
            else:
                self.explainer_type = "Tree Feature Importances"
        else:
            self.explainer_type = "UnsupportedModel"

    def explain_instance(
        self,
        processed_vector: np.ndarray,
        model_version: str = "xgboost-v1.0",
        prediction: str = "BENIGN",
        confidence: Optional[float] = None,
        top_n: int = 5
    ) -> Dict[str, Any]:
        """
        Computes structured SHAP feature attributions for a processed input vector.
        Supports dual Phase 4/5 legacy & Phase 6 strict contract keys:
          explanation_available / available: bool
          explanation_method: Optional[str]
          reason: Optional[str]
          explainer_type: str
          model_version: str
          prediction: str
          confidence: Optional[float]
          timestamp: str
          xai_latency_ms: float
          features / top_features: List[Dict[str, Any]]
        """
        t0 = time.time()
        timestamp = datetime.now(timezone.utc).isoformat()

        if processed_vector.ndim == 1:
            processed_vector = processed_vector.reshape(1, -1)

        num_features = processed_vector.shape[1]
        feature_labels = self.feature_names[:num_features] if len(self.feature_names) >= num_features else [f"Feature_{i}" for i in range(num_features)]

        # Check for unsupported model architecture
        model_obj = getattr(self.model, "model", self.model)
        model_type_name = type(model_obj).__name__
        model_type = model_type_name.lower()

        if self.explainer_type == "UnsupportedModel":
            t_exec = (time.time() - t0) * 1000.0
            reason_msg = f"Model architecture '{model_type_name}' is not supported for Tree SHAP explainability."
            return {
                "explanation_available": False,
                "available": False,
                "explanation_method": None,
                "reason": reason_msg,
                "explainer_type": self.explainer_type,
                "model_version": model_version,
                "prediction": prediction,
                "confidence": round(confidence, 4) if confidence is not None else None,
                "timestamp": timestamp,
                "xai_latency_ms": round(t_exec, 2),
                "features": [],
                "top_features": []
            }

        # 1. CatBoost Native Exact SHAP Feature Attributions
        if "catboost" in model_type:
            try:
                from catboost import Pool
                cb_pool = Pool(processed_vector)
                shap_vals = model_obj.get_feature_importance(cb_pool, type="ShapValues")
                if shap_vals.ndim == 3:
                    vals = shap_vals[0, 0, :-1]
                elif shap_vals.ndim == 2:
                    vals = shap_vals[0, :-1]
                else:
                    vals = shap_vals[:-1]

                feature_items = []
                for i in range(min(num_features, len(vals))):
                    contrib = float(vals[i])
                    input_val = float(processed_vector[0, i])
                    feature_items.append({
                        "feature": feature_labels[i],
                        "input_value": round(input_val, 4),
                        "contribution": round(contrib, 4),
                        "direction": "positive" if contrib >= 0 else "negative"
                    })

                feature_items = sorted(feature_items, key=lambda item: abs(item["contribution"]), reverse=True)[:top_n]
                for rank, item in enumerate(feature_items, 1):
                    item["rank"] = rank

                t_exec = (time.time() - t0) * 1000.0
                return {
                    "explanation_available": True,
                    "available": True,
                    "explanation_method": "SHAP TreeExplainer",
                    "reason": None,
                    "explainer_type": "SHAP TreeExplainer",
                    "model_version": model_version,
                    "prediction": prediction,
                    "confidence": round(confidence, 4) if confidence is not None else None,
                    "timestamp": timestamp,
                    "xai_latency_ms": round(t_exec, 2),
                    "features": feature_items,
                    "top_features": feature_items
                }
            except Exception as e:
                logger.warning(f"CatBoost native SHAP calculation failed: {e}")

        # 2. General SHAP TreeExplainer Evaluation
        if HAS_SHAP and self.explainer is not None and self.explainer != "catboost_native":
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
                    input_val = float(processed_vector[0, i])
                    feature_items.append({
                        "feature": feature_labels[i],
                        "input_value": round(input_val, 4),
                        "contribution": round(contrib, 4),
                        "direction": "positive" if contrib >= 0 else "negative"
                    })

                feature_items = sorted(feature_items, key=lambda item: abs(item["contribution"]), reverse=True)[:top_n]
                for rank, item in enumerate(feature_items, 1):
                    item["rank"] = rank

                t_exec = (time.time() - t0) * 1000.0
                return {
                    "explanation_available": True,
                    "available": True,
                    "explanation_method": "SHAP TreeExplainer",
                    "reason": None,
                    "explainer_type": "SHAP TreeExplainer",
                    "model_version": model_version,
                    "prediction": prediction,
                    "confidence": round(confidence, 4) if confidence is not None else None,
                    "timestamp": timestamp,
                    "xai_latency_ms": round(t_exec, 2),
                    "features": feature_items,
                    "top_features": feature_items
                }
            except Exception as e:
                logger.error(f"SHAP explanation failed: {e}")

        # 2. Model Feature Importances Fallback for Tree Models
        if hasattr(model_obj, "feature_importances_"):
            try:
                importances = model_obj.feature_importances_
                if len(importances) == num_features:
                    weights = importances * processed_vector[0]
                    feature_items = []
                    for i in range(num_features):
                        contrib = float(weights[i])
                        input_val = float(processed_vector[0, i])
                        feature_items.append({
                            "feature": feature_labels[i],
                            "input_value": round(input_val, 4),
                            "contribution": round(contrib, 4),
                            "direction": "positive" if contrib >= 0 else "negative"
                        })

                    feature_items = sorted(feature_items, key=lambda item: abs(item["contribution"]), reverse=True)[:top_n]
                    for rank, item in enumerate(feature_items, 1):
                        item["rank"] = rank

                    t_exec = (time.time() - t0) * 1000.0
                    return {
                        "explanation_available": True,
                        "available": True,
                        "explanation_method": "Tree Feature Importances",
                        "reason": None,
                        "explainer_type": "Tree Feature Importances",
                        "model_version": model_version,
                        "prediction": prediction,
                        "confidence": round(confidence, 4) if confidence is not None else None,
                        "timestamp": timestamp,
                        "xai_latency_ms": round(t_exec, 2),
                        "features": feature_items,
                        "top_features": feature_items
                    }
            except Exception as e:
                logger.error(f"Feature importances explanation failed: {e}")

        # Controlled explanation failure (No fake data)
        t_exec = (time.time() - t0) * 1000.0
        return {
            "explanation_available": False,
            "available": False,
            "explanation_method": None,
            "reason": f"Explainer computation failed for model '{model_type_name}'.",
            "explainer_type": "None",
            "model_version": model_version,
            "prediction": prediction,
            "confidence": round(confidence, 4) if confidence is not None else None,
            "timestamp": timestamp,
            "xai_latency_ms": round(t_exec, 2),
            "features": [],
            "top_features": []
        }
