"""
backend/app/services/behavior_baseline_service.py
=================================================
Phase 3.8 Explainable Statistical Behavioral Baseline Engine.
Computes rolling averages, sample standard deviations, z-score deviations, and anomaly scores.
"""

from typing import Dict, Any, List, Optional
import math
import logging
from datetime import datetime, timezone

logger = logging.getLogger("SentinelAI")


class BehaviorBaselineEngine:
    """Statistical anomaly engine computing explainable metric deviations."""

    @staticmethod
    def calculate_deviation(
        metric_name: str,
        observed_value: float,
        baseline_mean: float,
        baseline_std: float,
        threshold_z: float = 2.5
    ) -> Dict[str, Any]:
        """
        Calculates explainable z-score deviation against baseline mean and standard deviation.
        """
        safe_std = max(baseline_std, 0.001)
        z_score = round((observed_value - baseline_mean) / safe_std, 4)
        deviation_pct = round(((observed_value - baseline_mean) / max(abs(baseline_mean), 0.001)) * 100.0, 2)

        is_anomalous = abs(z_score) >= threshold_z
        if abs(z_score) >= 4.0:
            severity = "CRITICAL"
            anomaly_score = min(100.0, 75.0 + (abs(z_score) - 4.0) * 10.0)
        elif abs(z_score) >= 3.0:
            severity = "HIGH"
            anomaly_score = 50.0 + (abs(z_score) - 3.0) * 25.0
        elif abs(z_score) >= threshold_z:
            severity = "MEDIUM"
            anomaly_score = 25.0 + (abs(z_score) - threshold_z) * 25.0
        else:
            severity = "LOW"
            anomaly_score = max(0.0, (abs(z_score) / threshold_z) * 25.0)

        anomaly_score = round(anomaly_score, 2)

        if is_anomalous:
            explanation = (
                f"Metric '{metric_name}' observed value {observed_value:.2f} deviates by {z_score:+.2f} "
                f"standard deviations from baseline mean {baseline_mean:.2f} ({deviation_pct:+.1f}% deviation)."
            )
        else:
            explanation = (
                f"Metric '{metric_name}' observed value {observed_value:.2f} is within normal operational "
                f"limits (z-score: {z_score:+.2f}, baseline mean: {baseline_mean:.2f})."
            )

        return {
            "metric_name": metric_name,
            "observed_value": observed_value,
            "baseline_mean": baseline_mean,
            "baseline_std": baseline_std,
            "z_score": z_score,
            "deviation_percentage": deviation_pct,
            "is_anomalous": is_anomalous,
            "anomaly_score": anomaly_score,
            "severity": severity,
            "explanation": explanation
        }

    @staticmethod
    def compute_rolling_baseline(values: List[float]) -> Dict[str, float]:
        """Calculates mean, standard deviation, and sample count for a series of historical observations."""
        if not values:
            return {"mean": 0.0, "std": 1.0, "count": 0}

        count = len(values)
        mean = sum(values) / count
        if count > 1:
            variance = sum((x - mean) ** 2 for x in values) / (count - 1)
            std = math.sqrt(variance)
        else:
            std = 1.0

        return {
            "mean": round(mean, 4),
            "std": round(std, 4),
            "min": round(min(values), 4),
            "max": round(max(values), 4),
            "count": count
        }
