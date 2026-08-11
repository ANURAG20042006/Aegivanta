import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from scipy import stats


class AccumulatedWindowDriftDetector:
    """
    Accumulated Window Drift Monitoring Engine:
    Maintains a production window of incoming feature observations and performs
    Kolmogorov-Smirnov (KS) and Population Stability Index (PSI) tests against stored baseline distributions.
    """

    def __init__(
        self,
        baseline_distribution: Optional[np.ndarray] = None,
        feature_names: Optional[List[str]] = None,
        window_size: int = 50,
        psi_threshold: float = 0.25,
        ks_alpha: float = 0.05
    ):
        self.baseline_distribution = baseline_distribution
        self.feature_names = feature_names or []
        self.window_size = window_size
        self.psi_threshold = psi_threshold
        self.ks_alpha = ks_alpha
        self.production_window: List[np.ndarray] = []

    def update_baseline(self, baseline_matrix: np.ndarray, feature_names: List[str]):
        """Sets baseline training distribution matrix."""
        self.baseline_distribution = baseline_matrix
        self.feature_names = feature_names
        self.production_window.clear()

    def add_observation(self, feature_vector: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Accumulates a production feature vector observation.
        Triggers drift evaluation once window_size observations are accumulated.
        """
        vec = feature_vector.flatten()
        self.production_window.append(vec)

        if len(self.production_window) >= self.window_size:
            results = self.evaluate_drift()
            self.production_window.clear()  # Reset window after evaluation
            return results

        return None

    def calculate_psi(self, baseline: np.ndarray, current: np.ndarray, num_bins: int = 10) -> float:
        """Calculates Population Stability Index (PSI) between baseline and current observations."""
        try:
            quantiles = np.linspace(0, 100, num_bins + 1)
            bins = np.percentile(baseline, quantiles)
            bins[0] -= 1e-5
            bins[-1] += 1e-5
            
            baseline_counts, _ = np.histogram(baseline, bins=bins)
            current_counts, _ = np.histogram(current, bins=bins)
            
            baseline_pct = baseline_counts / len(baseline)
            current_pct = current_counts / len(current)
            
            # Replace zeros with epsilon to avoid div by zero / log(0)
            eps = 1e-4
            baseline_pct = np.where(baseline_pct == 0, eps, baseline_pct)
            current_pct = np.where(current_pct == 0, eps, current_pct)
            
            psi_val = np.sum((current_pct - baseline_pct) * np.log(current_pct / baseline_pct))
            return float(psi_val)
        except Exception:
            return 0.0

    def evaluate_drift(self) -> Dict[str, Any]:
        """Runs KS and PSI drift evaluation across all features."""
        if self.baseline_distribution is None or len(self.production_window) == 0:
            return {"drift_detected": False, "reason": "Insufficient baseline or window data"}

        curr_matrix = np.array(self.production_window)
        num_features = min(self.baseline_distribution.shape[1], curr_matrix.shape[1])
        
        drifted_features = []
        feature_psi_scores = {}
        feature_ks_pvalues = {}

        for i in range(num_features):
            base_col = self.baseline_distribution[:, i]
            curr_col = curr_matrix[:, i]

            # 1. KS Test
            ks_stat, p_val = stats.ks_2samp(base_col, curr_col)
            feature_ks_pvalues[i] = round(float(p_val), 4)

            # 2. PSI Test
            psi_val = self.calculate_psi(base_col, curr_col)
            feature_psi_scores[i] = round(psi_val, 4)

            # Flag feature as drifted if PSI > threshold or KS p_value < alpha
            if psi_val > self.psi_threshold or p_val < self.ks_alpha:
                feat_name = self.feature_names[i] if i < len(self.feature_names) else f"Feature_{i}"
                drifted_features.append(feat_name)

        drift_detected = len(drifted_features) > 0
        severity = "CRITICAL" if len(drifted_features) > (num_features / 2) else "WARNING" if drift_detected else "NORMAL"

        return {
            "drift_detected": drift_detected,
            "severity": severity,
            "sample_window_size": len(self.production_window),
            "drifted_features_count": len(drifted_features),
            "drifted_features": drifted_features,
            "message": f"DATA DRIFT DETECTED across {len(drifted_features)} features" if drift_detected else "Feature distribution remains stable within baseline limits"
        }
