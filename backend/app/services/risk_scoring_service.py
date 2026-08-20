"""
backend/app/services/risk_scoring_service.py
============================================
Phase 3.6 Deterministic Risk-Based Alert & Incident Prioritization Service.
Computes explainable, mathematically bounded risk scores (0–100) across 8 orthogonal dimensions.
"""

from typing import Dict, Any, Tuple
import math


class RiskScoringService:
    """
    Computes deterministic, explainable risk scores for security detections and incidents.
    Bands:
      0–24:   LOW
      25–49:  MEDIUM
      50–74:  HIGH
      75–100: CRITICAL
    """

    SEVERITY_BASE_SCORES = {
        "INFORMATIONAL": 5.0,
        "LOW": 20.0,
        "MEDIUM": 45.0,
        "HIGH": 75.0,
        "CRITICAL": 95.0
    }

    ASSET_CRITICALITY_BOOST = {
        "LOW": 0.0,
        "MEDIUM": 5.0,
        "HIGH": 12.0,
        "CRITICAL": 20.0
    }

    @staticmethod
    def classify_score_band(score: float) -> str:
        """Categorizes 0-100 numeric score into standardized severity tier."""
        if score >= 75.0:
            return "CRITICAL"
        elif score >= 50.0:
            return "HIGH"
        elif score >= 25.0:
            return "MEDIUM"
        return "LOW"

    @classmethod
    def calculate_incident_risk(
        cls,
        severity: str = "MEDIUM",
        confidence: float = 0.85,
        ioc_match_count: int = 0,
        max_ioc_confidence: float = 0.0,
        asset_criticality: str = "MEDIUM",
        affected_asset_count: int = 1,
        event_count: int = 1,
        hop_count: int = 1,
        crown_jewel_index: float = 0.0,
        blast_radius_score: float = 0.0,
        has_lateral_movement: bool = False,
        velocity_events_per_minute: float = 1.0
    ) -> Tuple[float, str, Dict[str, Any]]:
        """
        Calculates explainable multi-signal risk score and returns:
        (normalized_score, classification_band, component_breakdown_dict)
        """
        # 1. Base Severity Contribution (Weight: 35%)
        sev_key = severity.upper()
        base_sev = cls.SEVERITY_BASE_SCORES.get(sev_key, 45.0)
        c_sev = base_sev * 0.35

        # 2. Confidence Contribution (Weight: 15%)
        conf_clamped = min(max(float(confidence), 0.1), 1.0)
        c_conf = (conf_clamped * 100.0) * 0.15

        # 3. IOC & Threat Intelligence Contribution (Weight: 15%)
        ioc_score = 0.0
        if ioc_match_count > 0:
            ioc_score = min(max_ioc_confidence * 80.0 + min(ioc_match_count * 10.0, 20.0), 100.0)
        c_ioc = ioc_score * 0.15

        # 4. Asset Criticality & Scope Contribution (Weight: 15%)
        asset_crit_boost = cls.ASSET_CRITICALITY_BOOST.get(asset_criticality.upper(), 5.0)
        asset_scope_score = min(asset_crit_boost * 3.0 + min(affected_asset_count * 10.0, 40.0), 100.0)
        c_asset = asset_scope_score * 0.15

        # 5. Lateral Movement & Graph Traversal Contribution (Weight: 10%)
        lateral_score = 0.0
        if has_lateral_movement or hop_count >= 2:
            lateral_score = min(50.0 + (hop_count * 15.0), 100.0)
        c_lateral = lateral_score * 0.10

        # 6. Crown Jewel & Blast Radius Contribution (Weight: 10%)
        blast_score = min(crown_jewel_index * 0.6 + blast_radius_score * 0.4, 100.0)
        c_blast = blast_score * 0.10

        # Raw cumulative score
        raw_score = c_sev + c_conf + c_ioc + c_asset + c_lateral + c_blast

        # Multi-event frequency multiplier (+up to 10 points for sustained attacks)
        if event_count > 1:
            freq_boost = min(math.log2(event_count) * 2.5, 10.0)
            raw_score += freq_boost

        # High velocity burst modifier (+up to 5 points)
        if velocity_events_per_minute > 60.0:
            raw_score += min((velocity_events_per_minute / 60.0) * 2.0, 5.0)

        # Final score normalization [0.0 - 100.0]
        final_score = round(min(max(raw_score, 0.0), 100.0), 2)
        band = cls.classify_score_band(final_score)

        components = {
            "base_severity_contribution": round(c_sev, 2),
            "confidence_contribution": round(c_conf, 2),
            "threat_intel_contribution": round(c_ioc, 2),
            "asset_criticality_contribution": round(c_asset, 2),
            "lateral_movement_contribution": round(c_lateral, 2),
            "blast_radius_contribution": round(c_blast, 2),
            "total_normalized_score": final_score,
            "classification_band": band
        }

        return final_score, band, components
