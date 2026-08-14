"""
backend/app/services/anomaly_service.py
======================================
Behavioral Baselines & Explainable Anomaly Detection Engine.
Calculates asset-specific rolling statistical thresholds with zero-variance protection,
cold-start management, directional classification, and alert suppression debouncing.
"""

import math
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.behavioral import BehavioralBaseline, AnomalyEvent
from backend.app.core.logging import logger


MIN_BASELINE_SAMPLES = 5
DEBOUNCE_WINDOW_SECONDS = 60

# Configurable metric deviation thresholds
METRIC_Z_THRESHOLDS: Dict[str, float] = {
    "packet_rate": 3.0,
    "byte_volume": 3.0,
    "destination_diversity": 3.0,
    "flow_duration": 3.5,
    "error_rate_pct": 2.5,
}
DEFAULT_Z_THRESHOLD = 3.0


class AnomalyService:
    """Asset-Specific Behavioral Baseline & Anomaly Detection Service."""

    @staticmethod
    async def update_baseline(
        asset_id: str,
        metric_name: str,
        value: float,
        db: AsyncSession
    ) -> Optional[BehavioralBaseline]:
        """
        Updates rolling baseline statistics (mean, standard deviation, sample count)
        for an asset dimension using Welford's online incremental algorithm.
        """
        if value is None or math.isnan(value) or math.isinf(value):
            return None

        query = select(BehavioralBaseline).where(
            BehavioralBaseline.asset_id == asset_id,
            BehavioralBaseline.metric_name == metric_name
        )
        res = await db.execute(query)
        baseline = res.scalar_one_or_none()

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if not baseline:
            baseline = BehavioralBaseline(
                asset_id=asset_id,
                metric_name=metric_name,
                baseline_mean=float(value),
                baseline_std=0.5,
                min_val=float(value),
                max_val=float(value),
                sample_count=1,
                updated_at=now
            )
            db.add(baseline)
        else:
            n = baseline.sample_count + 1
            old_mean = baseline.baseline_mean
            new_mean = old_mean + (value - old_mean) / n
            
            # Welford's algorithm for rolling variance
            old_var = baseline.baseline_std ** 2
            new_var = ((n - 1) * old_var + (value - old_mean) * (value - new_mean)) / max(n, 1)
            new_std = max(math.sqrt(max(new_var, 0.001)), 0.1)

            baseline.baseline_mean = round(new_mean, 3)
            baseline.baseline_std = round(new_std, 3)
            baseline.min_val = min(baseline.min_val if baseline.min_val is not None else value, value)
            baseline.max_val = max(baseline.max_val if baseline.max_val is not None else value, value)
            baseline.sample_count = n
            baseline.updated_at = now

        await db.flush()
        return baseline

    @staticmethod
    async def detect_anomaly(
        asset_id: str,
        metric_name: str,
        observed_value: float,
        db: AsyncSession
    ) -> Optional[AnomalyEvent]:
        """
        Evaluates an observed metric against the asset's behavioral baseline.
        Applies:
          - NaN / Inf rejection
          - Cold-Start guard (MIN_BASELINE_SAMPLES)
          - Zero / near-zero standard deviation fallback
          - Directional categorization (SPIKE_INCREASE vs DROP_DECREASE)
          - Metric-specific configurable thresholds
          - Alert debounce window
        """
        if observed_value is None or math.isnan(observed_value) or math.isinf(observed_value):
            return None

        query = select(BehavioralBaseline).where(
            BehavioralBaseline.asset_id == asset_id,
            BehavioralBaseline.metric_name == metric_name
        )
        res = await db.execute(query)
        baseline = res.scalar_one_or_none()

        # 1. Cold-Start Guard: Require minimum baseline observations
        if not baseline or baseline.sample_count < MIN_BASELINE_SAMPLES:
            await AnomalyService.update_baseline(asset_id, metric_name, observed_value, db)
            return None

        mean = baseline.baseline_mean
        std = max(baseline.baseline_std, 0.1)

        # 2. Near-Zero Variance Protection
        if std < 0.2:
            # Deterministic relative deviation rule for constant baselines
            if mean > 0:
                rel_diff = abs(observed_value - mean) / mean
                z_score = (observed_value - mean) / (mean * 0.1) if rel_diff > 0.5 else 0.0
            else:
                z_score = observed_value / 0.5 if abs(observed_value) > 1.0 else 0.0
        else:
            z_score = (observed_value - mean) / std

        # Update baseline after computing deviation
        await AnomalyService.update_baseline(asset_id, metric_name, observed_value, db)

        # 3. Configurable Threshold Check
        threshold = METRIC_Z_THRESHOLDS.get(metric_name, DEFAULT_Z_THRESHOLD)
        if abs(z_score) < threshold:
            return None

        # 4. Debounce / Alert Storm Suppression
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        debounce_cutoff = now - timedelta(seconds=DEBOUNCE_WINDOW_SECONDS)
        recent_query = select(AnomalyEvent).where(
            AnomalyEvent.asset_id == asset_id,
            AnomalyEvent.metric_name == metric_name,
            AnomalyEvent.timestamp >= debounce_cutoff
        ).limit(1)
        recent_res = await db.execute(recent_query)
        if recent_res.scalar_one_or_none():
            # Suppress duplicate anomaly event within debounce window
            return None

        # 5. Directionality & Score Calculation
        direction = "SPIKE_INCREASE" if z_score > 0 else "DROP_DECREASE"
        anomaly_score = min(100.0, max(0.0, 50.0 + (abs(z_score) - threshold) * 12.5))
        
        # Severity Classification
        if abs(z_score) >= 5.0:
            severity = "CRITICAL"
        elif abs(z_score) >= 4.0:
            severity = "HIGH"
        else:
            severity = "MEDIUM"

        # Deterministic English Rationale
        ratio = round(observed_value / max(mean, 0.01), 1) if mean > 0 else round(abs(z_score), 1)
        dir_word = "increased" if z_score > 0 else "dropped"
        explanation = (
            f"Metric '{metric_name}' ({observed_value:.1f}) {dir_word} {ratio}x [{direction}] "
            f"relative to asset baseline ({mean:.1f} \u00b1 {std:.1f}, z-score: {z_score:.2f}, threshold: {threshold}\u03c3)."
        )

        anomaly = AnomalyEvent(
            asset_id=asset_id,
            timestamp=now,
            metric_name=metric_name,
            observed_value=float(observed_value),
            baseline_mean=mean,
            baseline_std=std,
            z_score=round(z_score, 2),
            anomaly_score=round(anomaly_score, 1),
            severity=severity,
            explanation=explanation,
            status="ACTIVE"
        )
        db.add(anomaly)
        await db.flush()

        # Broadcast WebSocket telemetry
        try:
            from backend.app.api.v1.websocket import manager
            await manager.broadcast({
                "type": "ANOMALY_DETECTED",
                "data": {
                    "anomaly_id": anomaly.id,
                    "asset_id": asset_id,
                    "metric_name": metric_name,
                    "observed_value": observed_value,
                    "direction": direction,
                    "z_score": round(z_score, 2),
                    "anomaly_score": round(anomaly_score, 1),
                    "severity": severity,
                    "explanation": explanation,
                    "timestamp": now.isoformat()
                }
            })
        except Exception:
            pass

        return anomaly
