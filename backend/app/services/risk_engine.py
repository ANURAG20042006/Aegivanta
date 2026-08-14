"""
backend/app/services/risk_engine.py
===================================
Deterministic, Transparent Operational Risk Scoring Engine for SentinelAI.

Calculates normalized 0–100 operational risk scores based on:
1. Threat Severity (Weight: 40%)
2. Model Detection Confidence (Weight: 25%)
3. Protected Asset Criticality (Weight: 20%)
4. Alert Recurrence / Attack Frequency (Weight: 15%)

Operational Tiers:
- 0–24:   LOW
- 25–49:  MEDIUM
- 50–74:  HIGH
- 75–100: CRITICAL
"""

from typing import Dict, Any, Optional


SEVERITY_WEIGHTS: Dict[str, float] = {
    "CRITICAL": 1.0,
    "HIGH": 0.75,
    "MEDIUM": 0.50,
    "LOW": 0.25,
    "INFO": 0.05,
}

CRITICALITY_WEIGHTS: Dict[str, float] = {
    "CRITICAL": 1.0,
    "HIGH": 0.75,
    "MEDIUM": 0.50,
    "LOW": 0.25,
}


class RiskScoringEngine:
    """
    Computes deterministic operational risk scores for security alerts,
    incidents, and protected assets.
    """

    @staticmethod
    def calculate_risk_score(
        severity: str,
        confidence: Optional[float] = None,
        criticality: str = "medium",
        alert_count: int = 1
    ) -> float:
        """
        Calculates a normalized 0.0–100.0 operational risk score.
        
        Formula:
          Base = (Severity_Weight * 40.0) + (Confidence * 25.0) + 
                 (Criticality_Weight * 20.0) + (Recurrence_Factor * 15.0)
        """
        sev_w = SEVERITY_WEIGHTS.get(severity.upper(), 0.5)
        
        # If model confidence is unavailable, default safely to 0.5
        conf_w = float(confidence) if confidence is not None else 0.5
        conf_w = max(0.0, min(1.0, conf_w))
        
        crit_w = CRITICALITY_WEIGHTS.get(criticality.upper(), 0.5)
        
        # Recurrence factor saturates at 10 alerts
        recurrence_w = min(1.0, max(1, alert_count) / 10.0)
        
        raw_score = (sev_w * 40.0) + (conf_w * 25.0) + (crit_w * 20.0) + (recurrence_w * 15.0)
        normalized = round(max(0.0, min(100.0, raw_score)), 1)
        return normalized

    @staticmethod
    def get_risk_tier(score: float) -> str:
        """Returns the operational tier label for a numeric risk score."""
        if score >= 75.0:
            return "CRITICAL"
        elif score >= 50.0:
            return "HIGH"
        elif score >= 25.0:
            return "MEDIUM"
        return "LOW"

    @classmethod
    def get_score_breakdown(
        cls,
        severity: str,
        confidence: Optional[float] = None,
        criticality: str = "medium",
        alert_count: int = 1
    ) -> Dict[str, Any]:
        """Provides full mathematical transparency for SOC auditability."""
        sev_w = SEVERITY_WEIGHTS.get(severity.upper(), 0.5)
        conf_w = float(confidence) if confidence is not None else 0.5
        conf_w = max(0.0, min(1.0, conf_w))
        crit_w = CRITICALITY_WEIGHTS.get(criticality.upper(), 0.5)
        recurrence_w = min(1.0, max(1, alert_count) / 10.0)
        
        score = cls.calculate_risk_score(severity, confidence, criticality, alert_count)
        
        return {
            "risk_score": score,
            "tier": cls.get_risk_tier(score),
            "components": {
                "severity_contribution": round(sev_w * 40.0, 2),
                "confidence_contribution": round(conf_w * 25.0, 2),
                "criticality_contribution": round(crit_w * 20.0, 2),
                "recurrence_contribution": round(recurrence_w * 15.0, 2)
            },
            "formula": "Score = (Severity_Weight * 40) + (Confidence * 25) + (Criticality_Weight * 20) + (Recurrence_Factor * 15)"
        }
