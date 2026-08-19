"""
backend/app/services/ensemble_service.py
========================================
Phase 2 Advanced Multi-Model Ensemble Detection & Confidence Calibration Engine.
Provides deterministic aggregation (Soft Voting, Hard Voting, Weighted Confidence)
across production models with model agreement telemetry and confidence calibration.
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from collections import Counter

from backend.app.config import settings

logger = logging.getLogger("SentinelAI")


class EnsembleStrategy:
    SOFT_VOTING = "SOFT_VOTING"
    HARD_VOTING = "HARD_VOTING"
    WEIGHTED_CONFIDENCE = "WEIGHTED_CONFIDENCE"
    CHAMPION_FALLBACK = "CHAMPION_FALLBACK"


class ConfidenceCalibrator:
    """
    Parametric temperature-based and piecewise linear confidence calibrator.
    Maps raw tree/ensemble probabilities to empirical calibrated confidence scores.
    """

    DEFAULT_TEMPERATURE = 1.15  # Softens over-confident tree ensemble predictions

    @classmethod
    def calibrate(cls, raw_prob: float, temperature: float = DEFAULT_TEMPERATURE) -> float:
        """Applies temperature scaling logit calibration to a probability in [0, 1]."""
        if raw_prob <= 0.0:
            return 0.0
        if raw_prob >= 1.0:
            return 1.0

        # Logit transform
        eps = 1e-7
        p = np.clip(raw_prob, eps, 1.0 - eps)
        logit = np.log(p / (1.0 - p))
        scaled_logit = logit / max(0.1, temperature)
        calibrated = 1.0 / (1.0 + np.exp(-scaled_logit))
        return round(float(calibrated), 4)


class EnsembleThreatDetector:
    """
    Authoritative Multi-Model Ensemble Threat Detector.
    Executes multiple production models and aggregates predictions with model agreement tracking.
    """

    DEFAULT_MODELS = ["CatBoost", "LightGBM", "Random Forest", "Decision Tree", "XGBoost"]

    def __init__(self, metadata_path: Optional[Path] = None):
        self.metadata_path = metadata_path
        self.model_weights: Dict[str, float] = {}
        self._load_weights_from_metadata()

    def _load_weights_from_metadata(self):
        """Loads benchmark cross-validation F1 scores as default ensemble weights."""
        if not self.metadata_path:
            base_dir = Path(settings.MODEL_ARTIFACTS_DIR)
            if not base_dir.is_absolute():
                base_dir = Path(__file__).resolve().parents[3] / base_dir
            self.metadata_path = base_dir / "metadata.json"

        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                for item in meta.get("leaderboard", []):
                    m_name = item["model_name"]
                    f1 = float(item.get("cv_f1_mean", 0.85) or 0.85)
                    self.model_weights[m_name] = max(0.1, f1)
            except Exception as e:
                logger.warning("Could not load ensemble weights from metadata.json: %s", e)

        # Fallback default weights if metadata missing
        if not self.model_weights:
            self.model_weights = {
                "CatBoost": 0.96,
                "LightGBM": 0.95,
                "Random Forest": 0.93,
                "XGBoost": 0.94,
                "Decision Tree": 0.88
            }

    def aggregate_predictions(
        self,
        predictions_map: Dict[str, Tuple[str, float, Dict[str, float]]],
        strategy: str = EnsembleStrategy.WEIGHTED_CONFIDENCE,
        temperature: float = 1.15
    ) -> Dict[str, Any]:
        """
        Aggregates individual model predictions into an auditable ensemble decision.

        Args:
            predictions_map: {model_name: (predicted_class, raw_confidence, class_probabilities)}
            strategy: Aggregation strategy (WEIGHTED_CONFIDENCE, SOFT_VOTING, HARD_VOTING)
            temperature: Temperature scaling parameter for calibration

        Returns:
            Dict containing:
              - final_prediction (str)
              - raw_confidence (float)
              - calibrated_confidence (float)
              - is_malicious (bool)
              - severity (str)
              - model_agreement_pct (float)
              - individual_predictions (dict)
              - individual_confidences (dict)
              - ensemble_strategy (str)
              - participating_models (list)
        """
        if not predictions_map:
            raise ValueError("predictions_map cannot be empty")

        participating_models = list(predictions_map.keys())
        individual_predictions = {m: res[0] for m, res in predictions_map.items()}
        individual_confidences = {m: round(float(res[1]), 4) for m, res in predictions_map.items()}

        # 1. Evaluate Class Voting & Model Agreement
        class_votes = Counter(individual_predictions.values())
        total_models = len(predictions_map)

        if strategy == EnsembleStrategy.HARD_VOTING:
            # Majority vote
            winning_class, win_votes = class_votes.most_common(1)[0]
            # Average confidence of models that voted for the winning class
            matching_confidences = [
                conf for m, conf in individual_confidences.items() if individual_predictions[m] == winning_class
            ]
            raw_conf = float(np.mean(matching_confidences)) if matching_confidences else 0.5
            agreement_pct = round((win_votes / total_models) * 100.0, 1)

        elif strategy == EnsembleStrategy.SOFT_VOTING:
            # Equal probability average across all classes
            all_classes = set()
            for _, _, probs in predictions_map.values():
                all_classes.update(probs.keys())

            class_scores = {c: 0.0 for c in all_classes}
            for _, _, probs in predictions_map.values():
                for c in all_classes:
                    class_scores[c] += probs.get(c, 0.0)

            winning_class = max(class_scores, key=class_scores.get)
            raw_conf = float(class_scores[winning_class] / total_models)
            win_votes = sum(1 for p in individual_predictions.values() if p == winning_class)
            agreement_pct = round((win_votes / total_models) * 100.0, 1)

        else:  # WEIGHTED_CONFIDENCE (Default)
            all_classes = set()
            for _, _, probs in predictions_map.values():
                all_classes.update(probs.keys())

            weighted_scores = {c: 0.0 for c in all_classes}
            total_weight = sum(self.model_weights.get(m, 1.0) for m in participating_models)

            for m, (_, _, probs) in predictions_map.items():
                w = self.model_weights.get(m, 1.0)
                for c in all_classes:
                    weighted_scores[c] += (probs.get(c, 0.0) * w)

            winning_class = max(weighted_scores, key=weighted_scores.get)
            raw_conf = float(weighted_scores[winning_class] / total_weight)
            win_votes = sum(1 for p in individual_predictions.values() if p == winning_class)
            agreement_pct = round((win_votes / total_models) * 100.0, 1)

        # 2. Calibrate Confidence
        calibrated_conf = ConfidenceCalibrator.calibrate(raw_conf, temperature=temperature)

        # 3. Determine Malicious Status & Severity
        is_malicious = (winning_class.upper() != "BENIGN")
        if not is_malicious:
            severity = "Low"
        elif calibrated_conf >= 0.90 or raw_conf >= 0.92:
            severity = "Critical"
        elif calibrated_conf >= 0.70 or raw_conf >= 0.75:
            severity = "High"
        elif calibrated_conf >= 0.40:
            severity = "Medium"
        else:
            severity = "Low"

        return {
            "final_prediction": winning_class,
            "raw_confidence": round(raw_conf, 4),
            "calibrated_confidence": calibrated_conf,
            "is_malicious": is_malicious,
            "severity": severity,
            "model_agreement_pct": agreement_pct,
            "participating_models": participating_models,
            "individual_predictions": individual_predictions,
            "individual_confidences": individual_confidences,
            "ensemble_strategy": strategy,
            "total_models_evaluated": total_models
        }


# Singleton Instance
ensemble_detector = EnsembleThreatDetector()
