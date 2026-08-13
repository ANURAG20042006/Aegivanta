import uuid
import hashlib
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
from scipy import stats


class AccumulatedWindowDriftDetector:
    """
    Phase 6 Production Drift Monitoring Engine:
    Accumulates incoming feature vectors in production windows and calculates:
      - DATA DRIFT (P(X)): Kolmogorov-Smirnov (KS) test, p-values, Population Stability Index (PSI) per feature.
      - PREDICTION DRIFT (P(Y_hat)): Shift in predicted class distribution.
      - CONCEPT / PERFORMANCE DRIFT (P(Y|X)): Ground-truth label performance metric decay (Accuracy).

    Standard Drift Status Levels:
      - NORMAL / NO_DRIFT: PSI < 0.25 and KS p-value >= 0.05
      - WARNING: 0.10 <= PSI < 0.25 or prediction shift > 0.20
      - DRIFT_DETECTED / CRITICAL: PSI >= 0.25 or concept drift / major feature decay

    Does NOT calculate drift from a single sample.
    Does NOT automatically promote candidate models to ACTIVE without promotion gate evaluation.
    """

    def __init__(
        self,
        reference_version: str = "schema-v1.0",
        baseline_distribution: Optional[np.ndarray] = None,
        baseline_predictions: Optional[List[str]] = None,
        feature_names: Optional[List[str]] = None,
        min_window_size: int = 50,
        window_size: Optional[int] = None,
        eval_interval: int = 50,
        psi_threshold: float = 0.25,
        ks_alpha: float = 0.05
    ):
        self.reference_version = reference_version
        self.baseline_distribution = baseline_distribution
        self.baseline_predictions = baseline_predictions or []
        self.feature_names = feature_names or []
        self.min_window_size = window_size if window_size is not None else min_window_size
        self.eval_interval = eval_interval
        self.psi_threshold = psi_threshold
        self.ks_alpha = ks_alpha
        self.baseline_hash: Optional[str] = None

        if baseline_distribution is not None:
            self._compute_baseline_hash()

        self.production_feature_window: List[np.ndarray] = []
        self.production_prediction_window: List[str] = []
        self.production_ground_truth_window: List[Tuple[str, str]] = []
        self.window_counter = 0

    def _compute_baseline_hash(self):
        if self.baseline_distribution is not None:
            raw_bytes = self.baseline_distribution.tobytes()
            self.baseline_hash = hashlib.sha256(raw_bytes).hexdigest()[:16]

    def update_baseline(
        self,
        baseline_matrix: np.ndarray,
        feature_names: List[str],
        baseline_predictions: Optional[List[str]] = None,
        reference_version: str = "schema-v1.0"
    ):
        """Sets reference baseline training distribution matrix and predictions."""
        self.reference_version = reference_version
        self.baseline_distribution = baseline_matrix
        self.feature_names = feature_names
        self.baseline_predictions = baseline_predictions or []
        self._compute_baseline_hash()
        self.production_feature_window.clear()
        self.production_prediction_window.clear()
        self.production_ground_truth_window.clear()

    def add_observation(
        self,
        feature_vector: np.ndarray,
        predicted_class: str = "BENIGN",
        ground_truth: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Accumulates a production feature observation.
        Triggers drift evaluation once min_window_size observations are accumulated.
        """
        vec = feature_vector.flatten()
        self.production_feature_window.append(vec)
        self.production_prediction_window.append(predicted_class)
        if ground_truth is not None:
            self.production_ground_truth_window.append((predicted_class, ground_truth))

        if len(self.production_feature_window) >= self.min_window_size:
            self.window_counter += 1
            results = self.evaluate_drift()
            self.production_feature_window.clear()
            self.production_prediction_window.clear()
            self.production_ground_truth_window.clear()
            return results

        return None

    def calculate_psi(self, baseline: np.ndarray, current: np.ndarray, num_bins: int = 10) -> float:
        """
        Calculates Population Stability Index (PSI) using 10-bin quantile/histogram strategy.
        PSI = sum((observed - expected) * ln(observed / expected))
        """
        try:
            quantiles = np.linspace(0, 100, num_bins + 1)
            bins = np.percentile(baseline, quantiles)
            bins[0] -= 1e-5
            bins[-1] += 1e-5

            bins = np.unique(bins)
            if len(bins) < 2:
                bins = np.array([baseline.min() - 1e-5, baseline.max() + 1e-5])

            baseline_counts, _ = np.histogram(baseline, bins=bins)
            current_counts, _ = np.histogram(current, bins=bins)

            baseline_pct = baseline_counts / max(len(baseline), 1)
            current_pct = current_counts / max(len(current), 1)

            eps = 1e-4
            baseline_pct = np.where(baseline_pct == 0, eps, baseline_pct)
            current_pct = np.where(current_pct == 0, eps, current_pct)

            psi_val = np.sum((current_pct - baseline_pct) * np.log(current_pct / baseline_pct))
            return float(psi_val)
        except Exception:
            return 0.0

    def evaluate_drift(self) -> Dict[str, Any]:
        """
        Evaluates Data Drift (P(X)), Prediction Drift (P(Y_hat)), and Concept Drift (P(Y|X)).
        Provides dual status fields for backward compatibility and Phase 6 specification:
          - alert_status: "NO_DRIFT", "WARNING", or "CRITICAL"
          - status: "NORMAL", "WARNING", or "DRIFT_DETECTED"
        """
        window_id = f"win-{self.window_counter}-{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        sample_count = len(self.production_feature_window)

        if self.baseline_distribution is None or sample_count == 0:
            return {
                "reference_version": self.reference_version,
                "baseline_hash": self.baseline_hash,
                "window_id": window_id,
                "timestamp": timestamp,
                "sample_count": sample_count,
                "status": "NORMAL",
                "alert_status": "NO_DRIFT",
                "drift_types": [],
                "reason": "Insufficient baseline or production window observations",
                "retraining_recommended": False
            }

        curr_matrix = np.array(self.production_feature_window)
        num_features = min(self.baseline_distribution.shape[1], curr_matrix.shape[1])

        # 1. DATA DRIFT EVALUATION
        affected_features = []
        feature_psi_scores = {}
        feature_ks_stats = {}
        feature_ks_pvalues = {}

        effective_alpha = self.ks_alpha / max(num_features, 1)
        max_feature_psi = 0.0

        for i in range(num_features):
            base_col = self.baseline_distribution[:, i]
            curr_col = curr_matrix[:, i]

            ks_stat, p_val = stats.ks_2samp(base_col, curr_col)
            psi_val = self.calculate_psi(base_col, curr_col)

            if psi_val > max_feature_psi:
                max_feature_psi = psi_val

            feature_name = self.feature_names[i] if i < len(self.feature_names) else f"Feature_{i}"
            feature_psi_scores[feature_name] = round(psi_val, 4)
            feature_ks_stats[feature_name] = round(float(ks_stat), 4)
            feature_ks_pvalues[feature_name] = round(float(p_val), 4)

            if psi_val >= self.psi_threshold or (p_val < effective_alpha and psi_val > 0.15):
                affected_features.append(feature_name)

        has_data_drift = len(affected_features) > 0

        # 2. PREDICTION DRIFT EVALUATION
        prediction_drift_detected = False
        prediction_dist_change = {}

        if self.baseline_predictions and len(self.production_prediction_window) > 0:
            base_unique, base_counts = np.unique(self.baseline_predictions, return_counts=True)
            curr_unique, curr_counts = np.unique(self.production_prediction_window, return_counts=True)

            base_dist = {str(k): float(v / len(self.baseline_predictions)) for k, v in zip(base_unique, base_counts)}
            curr_dist = {str(k): float(v / len(self.production_prediction_window)) for k, v in zip(curr_unique, curr_counts)}

            all_classes = set(base_dist.keys()).union(set(curr_dist.keys()))
            max_class_shift = 0.0
            for cls in all_classes:
                p_base = base_dist.get(cls, 0.0)
                p_curr = curr_dist.get(cls, 0.0)
                shift = abs(p_curr - p_base)
                prediction_dist_change[cls] = round(shift, 4)
                if shift > max_class_shift:
                    max_class_shift = shift

            if max_class_shift > 0.20:
                prediction_drift_detected = True

        # 3. CONCEPT / PERFORMANCE DRIFT EVALUATION
        concept_drift_detected = False
        performance_metrics = {}

        if len(self.production_ground_truth_window) >= 10:
            correct = sum(1 for p, g in self.production_ground_truth_window if p == g)
            accuracy = correct / len(self.production_ground_truth_window)
            performance_metrics["accuracy"] = round(accuracy, 4)
            if accuracy < 0.80:
                concept_drift_detected = True

        # Status Mapping
        if concept_drift_detected or len(affected_features) > (num_features // 3) or max_feature_psi >= 0.25:
            alert_status = "CRITICAL"
            status = "DRIFT_DETECTED"
        elif has_data_drift or prediction_drift_detected:
            alert_status = "WARNING"
            status = "WARNING"
        else:
            alert_status = "NO_DRIFT"
            status = "NORMAL"

        drift_types = []
        if has_data_drift:
            drift_types.append("DATA_DRIFT")
        if prediction_drift_detected:
            drift_types.append("PREDICTION_DRIFT")
        if concept_drift_detected:
            drift_types.append("CONCEPT_DRIFT")

        return {
            "reference_version": self.reference_version,
            "baseline_hash": self.baseline_hash,
            "window_id": window_id,
            "timestamp": timestamp,
            "sample_count": sample_count,
            "status": status,
            "alert_status": alert_status,
            "drift_types": drift_types,
            "retraining_recommended": (status == "DRIFT_DETECTED" or alert_status == "CRITICAL"),
            "thresholds": {
                "min_window_size": self.min_window_size,
                "ks_alpha": self.ks_alpha,
                "psi_threshold": self.psi_threshold
            },
            "statistics": {
                "max_feature_psi": round(max_feature_psi, 4),
                "affected_features_count": len(affected_features),
                "affected_features": affected_features,
                "psi_scores": feature_psi_scores,
                "ks_stats": feature_ks_stats,
                "ks_pvalues": feature_ks_pvalues,
                "prediction_distribution_change": prediction_dist_change,
                "performance_metrics": performance_metrics
            }
        }
