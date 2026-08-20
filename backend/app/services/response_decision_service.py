"""
backend/app/services/response_decision_service.py
=================================================
Phase 3.7 Automated Response Decision Engine.
Evaluates multi-dimensional threat signals (risk, severity, asset criticality, IOCs,
lateral movement, blast radius) to recommend actionable, policy-compliant containment strategies.
"""

from typing import Dict, Any, List, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.response_policy_service import ResponsePolicyEngine

logger = logging.getLogger("SentinelAI")


class ResponseDecisionService:
    """
    Automated decision service that selects appropriate response strategies
    and determines approval requirements.
    """

    @classmethod
    async def evaluate_incident_response(
        cls,
        incident_id: str,
        risk_score: float,
        severity: str,
        attack_type: str = "Threat Activity",
        asset_criticality: str = "MEDIUM",
        has_lateral_movement: bool = False,
        matched_iocs_count: int = 0,
        crown_jewel_index: float = 0.0,
        blast_radius_score: float = 0.0,
        source_ip: str = "0.0.0.0",
        destination_ip: str = "0.0.0.0",
        target_asset_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Determines the recommended response strategy and evaluates against policy.
        """
        # 1. Determine recommended action based on threat indicators
        recommended_actions: List[str] = []
        decision_reasons: List[str] = []

        att_upper = attack_type.upper()

        if has_lateral_movement or blast_radius_score >= 50.0 or crown_jewel_index >= 50.0:
            recommended_actions.append("ISOLATE_HOST")
            decision_reasons.append(f"Lateral movement or high blast radius ({blast_radius_score:.1f}%) warrants immediate host isolation.")

        if matched_iocs_count > 0 or "EXFIL" in att_upper or "DOS" in att_upper or "SCAN" in att_upper or "BRUTE" in att_upper:
            recommended_actions.append("BLOCK_IP")
            decision_reasons.append(f"Active threat indicator or attack pattern ({attack_type}) requires perimeter IP block on {source_ip}.")

        if "KERBER" in att_upper or "CRED" in att_upper or "AUTH" in att_upper or "PASSWORD" in att_upper:
            recommended_actions.append("REVOKE_SESSION")
            recommended_actions.append("DISABLE_ACCOUNT")
            decision_reasons.append("Credential manipulation detected; session revocation and account lockdown recommended.")

        if asset_criticality.upper() == "CRITICAL" or crown_jewel_index >= 70.0:
            recommended_actions.append("QUARANTINE_ASSET")
            decision_reasons.append("Critical Crown Jewel asset exposed in attack radius; asset quarantine recommended.")

        # Default fallback action
        if not recommended_actions:
            if severity.upper() in ["HIGH", "CRITICAL"]:
                recommended_actions.append("BLOCK_IP")
            else:
                recommended_actions.append("NOTIFY_ANALYST")

        # Deduplicate actions while preserving order
        unique_actions = list(dict.fromkeys(recommended_actions))
        primary_action = unique_actions[0]

        # 2. Evaluate Primary Action against Response Policy
        policy_eval = await ResponsePolicyEngine.evaluate(
            risk_score=risk_score,
            severity=severity,
            requested_action=primary_action,
            db=db
        )

        overall_decision = policy_eval["decision"]
        requires_approval = policy_eval["requires_approval"]
        is_allowed = policy_eval["is_allowed"]

        rationale = " ".join(decision_reasons) if decision_reasons else policy_eval["reason"]

        return {
            "incident_id": incident_id,
            "decision": overall_decision,
            "is_allowed": is_allowed,
            "requires_approval": requires_approval,
            "primary_recommended_action": primary_action,
            "all_recommended_actions": unique_actions,
            "allowed_actions": policy_eval.get("allowed_actions", []),
            "matched_policy": policy_eval.get("matched_policy_name", "DEFAULT"),
            "risk_score": risk_score,
            "severity": severity.upper(),
            "target_ip": source_ip,
            "target_asset_id": target_asset_id,
            "reason": rationale,
            "cooldown_seconds": policy_eval.get("cooldown_seconds", 300)
        }
