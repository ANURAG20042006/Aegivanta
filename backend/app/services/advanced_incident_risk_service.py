"""
backend/app/services/advanced_incident_risk_service.py
======================================================
Phase 26.5 Advanced Multi-Factor Incident Risk Engine.
Calculates transparent, explainable 0–100 dynamic incident risk scores based on 11 weighted factors:
1. Incident Base Severity (Weight: 15%)
2. Protected Asset Criticality (Weight: 15%)
3. Identity Privilege & Role (Weight: 10%)
4. Threat Intelligence IOC Reputation (Weight: 10%)
5. Lateral Movement & Multi-Hop Breadth (Weight: 10%)
6. Endpoint Zero-Trust Health & Posture (Weight: 10%)
7. ML Behavioral Anomaly Deviation (Weight: 10%)
8. Attack Chain Progression Stage (Weight: 10%)
9. Historical Recurrence Rate (Weight: 5%)
10. Detection Rule Confidence (Weight: 5%)
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("Aegivanta.AdvancedRisk")


class AdvancedIncidentRiskEngine:
    """Calculates multi-dimensional, transparent, and explainable 0–100 incident risk scores."""

    @classmethod
    def calculate_incident_risk(
        cls,
        severity: str = "HIGH",
        asset_criticality: str = "TIER_1_CRITICAL",
        identity_privilege: str = "ADMIN",
        ioc_confidence: float = 0.90,
        lateral_hops: int = 2,
        device_trust_score: float = 40.0,
        ml_anomaly_score: float = 0.88,
        attack_stage: str = "LATERAL_MOVEMENT",
        historical_recurrence_count: int = 3,
        detection_confidence: float = 0.95
    ) -> Dict[str, Any]:
        """
        Calculates an explainable 0-100 risk score with transparent per-factor breakdown.
        """
        # 1. Base Severity (0-100)
        sev_map = {"CRITICAL": 100.0, "HIGH": 75.0, "MEDIUM": 50.0, "LOW": 25.0, "INFORMATIONAL": 10.0}
        f_severity = sev_map.get(severity.upper(), 50.0)

        # 2. Asset Criticality (0-100)
        asset_map = {"TIER_1_CRITICAL": 100.0, "TIER_2_HIGH": 75.0, "TIER_3_MEDIUM": 50.0, "TIER_4_LOW": 25.0}
        f_asset = asset_map.get(asset_criticality.upper(), 50.0)

        # 3. Identity Privilege (0-100)
        priv_map = {"DOMAIN_ADMIN": 100.0, "ADMIN": 90.0, "ENGINEER": 60.0, "USER": 40.0, "SERVICE_ACCOUNT": 75.0}
        f_identity = priv_map.get(identity_privilege.upper(), 40.0)

        # 4. Threat Intel (0-100)
        f_ioc = min(100.0, max(0.0, ioc_confidence * 100.0))

        # 5. Lateral Movement Breadth (0-100)
        f_lateral = min(100.0, lateral_hops * 35.0)

        # 6. Endpoint Trust Inversion (Lower trust = Higher risk) (0-100)
        f_endpoint = max(0.0, 100.0 - device_trust_score)

        # 7. ML Anomaly Score (0-100)
        f_ml = min(100.0, max(0.0, ml_anomaly_score * 100.0))

        # 8. Attack Stage Progression (0-100)
        stage_map = {
            "RECONNAISSANCE": 20.0,
            "INITIAL_ACCESS": 40.0,
            "EXECUTION": 60.0,
            "PERSISTENCE": 70.0,
            "LATERAL_MOVEMENT": 85.0,
            "EXFILTRATION": 95.0,
            "IMPACT": 100.0
        }
        f_stage = stage_map.get(attack_stage.upper(), 50.0)

        # 9. Recurrence (0-100)
        f_recurrence = min(100.0, historical_recurrence_count * 20.0)

        # 10. Detection Confidence (0-100)
        f_confidence = min(100.0, max(0.0, detection_confidence * 100.0))

        # Weighted Composition (Total Weight: 100%)
        weighted_score = (
            f_severity * 0.15 +
            f_asset * 0.15 +
            f_identity * 0.10 +
            f_ioc * 0.10 +
            f_lateral * 0.10 +
            f_endpoint * 0.10 +
            f_ml * 0.10 +
            f_stage * 0.10 +
            f_recurrence * 0.05 +
            f_confidence * 0.05
        )

        final_score = round(max(0.0, min(100.0, weighted_score)), 1)

        # Categorize
        if final_score >= 85.0:
            category = "CRITICAL"
        elif final_score >= 65.0:
            category = "HIGH"
        elif final_score >= 40.0:
            category = "MEDIUM"
        else:
            category = "LOW"

        # Generate human-readable explanation
        reasons = []
        if f_severity >= 75.0:
            reasons.append(f"High base severity ({severity}) represents significant operational urgency.")
        if f_asset >= 75.0:
            reasons.append(f"Target is a critical infrastructure asset ({asset_criticality}).")
        if f_identity >= 75.0:
            reasons.append(f"Target account possesses elevated administrative privileges ({identity_privilege}).")
        if f_lateral >= 70.0:
            reasons.append(f"Multi-hop lateral movement observed across {lateral_hops} subnets.")
        if f_endpoint >= 50.0:
            reasons.append(f"Endpoint device posture is degraded (Trust Score: {device_trust_score}/100).")
        if f_stage >= 80.0:
            reasons.append(f"Attack chain reached advanced stage ({attack_stage}).")

        return {
            "risk_score": final_score,
            "risk_category": category,
            "factor_breakdown": {
                "base_severity": round(f_severity, 1),
                "asset_criticality": round(f_asset, 1),
                "identity_privilege": round(f_identity, 1),
                "threat_intelligence": round(f_ioc, 1),
                "lateral_movement": round(f_lateral, 1),
                "endpoint_posture": round(f_endpoint, 1),
                "ml_anomaly": round(f_ml, 1),
                "attack_stage": round(f_stage, 1),
                "historical_recurrence": round(f_recurrence, 1),
                "detection_confidence": round(f_confidence, 1)
            },
            "contributing_reasons": reasons,
            "business_impact_summary": f"High risk event impacting {asset_criticality} assets. Immediate containment required."
        }
