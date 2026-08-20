"""
backend/app/services/response_policy_service.py
===============================================
Phase 3.7 Centralized Response Policy Engine.
Evaluates incident risk, severity, action types, cooldowns, and authorization requirements.
"""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.response import ResponsePolicy

logger = logging.getLogger("SentinelAI")

DEFAULT_POLICIES = [
    {
        "id": "policy-default-low",
        "name": "POLICY_TIER_LOW_NO_AUTOMATION",
        "description": "Low severity events do not trigger automated remediation.",
        "minimum_risk_score": 0.0,
        "minimum_severity": "LOW",
        "allowed_actions": [],
        "requires_approval": False,
        "cooldown_seconds": 300,
        "max_actions_per_incident": 0,
        "allowed_target_types": ["IP", "HOST", "USER"]
    },
    {
        "id": "policy-default-medium",
        "name": "POLICY_TIER_MEDIUM_ALERT_ONLY",
        "description": "Medium severity alerts allow non-destructive notification actions.",
        "minimum_risk_score": 25.0,
        "minimum_severity": "MEDIUM",
        "allowed_actions": ["NOTIFY_ANALYST", "CREATE_TICKET"],
        "requires_approval": False,
        "cooldown_seconds": 300,
        "max_actions_per_incident": 3,
        "allowed_target_types": ["IP", "HOST", "USER"]
    },
    {
        "id": "policy-default-high",
        "name": "POLICY_TIER_HIGH_REQUIRE_APPROVAL",
        "description": "High severity incidents allow remediation with mandatory two-tier approval.",
        "minimum_risk_score": 50.0,
        "minimum_severity": "HIGH",
        "allowed_actions": ["BLOCK_IP", "ISOLATE_HOST", "QUARANTINE_ASSET", "REVOKE_SESSION"],
        "requires_approval": True,
        "cooldown_seconds": 180,
        "max_actions_per_incident": 5,
        "allowed_target_types": ["IP", "HOST", "ASSET", "USER"]
    },
    {
        "id": "policy-default-critical",
        "name": "POLICY_TIER_CRITICAL_AUTOMATED",
        "description": "Critical incidents allow immediate containment actions with strict validation.",
        "minimum_risk_score": 75.0,
        "minimum_severity": "CRITICAL",
        "allowed_actions": ["BLOCK_IP", "ISOLATE_HOST", "QUARANTINE_ASSET", "REVOKE_SESSION", "DISABLE_ACCOUNT"],
        "requires_approval": True,
        "cooldown_seconds": 60,
        "max_actions_per_incident": 10,
        "allowed_target_types": ["IP", "HOST", "ASSET", "USER"]
    }
]


class ResponsePolicyEngine:
    """Centralized policy engine for evaluating SOAR response decisions."""

    SEVERITY_ORDER = {"INFORMATIONAL": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

    @classmethod
    async def get_active_policies(cls, db: Optional[AsyncSession] = None) -> List[Dict[str, Any]]:
        """Fetches active policies from the database or returns built-in defaults."""
        if db:
            try:
                res = await db.execute(select(ResponsePolicy).where(ResponsePolicy.enabled == True))
                db_policies = res.scalars().all()
                if db_policies and hasattr(db_policies[0], "minimum_risk_score"):
                    return [
                        {
                            "id": p.id,
                            "name": p.name,
                            "description": p.description,
                            "minimum_risk_score": p.minimum_risk_score,
                            "minimum_severity": p.minimum_severity,
                            "allowed_actions": p.allowed_actions or [],
                            "requires_approval": p.requires_approval,
                            "cooldown_seconds": p.cooldown_seconds,
                            "max_actions_per_incident": p.max_actions_per_incident,
                            "allowed_target_types": p.allowed_target_types or []
                        }
                        for p in db_policies
                    ]
            except Exception as e:
                logger.debug("Database policy lookup fallback: %s", e)

        return DEFAULT_POLICIES

    @classmethod
    async def evaluate(
        cls,
        risk_score: float,
        severity: str,
        requested_action: Optional[str] = None,
        target_type: str = "IP",
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Evaluates risk score, severity, and requested action against active response policies.
        Returns:
        {
            "decision": "ALLOW" | "REQUIRE_APPROVAL" | "DENY_NO_AUTOMATION" | "DENY_ACTION_UNSUPPORTED",
            "is_allowed": bool,
            "requires_approval": bool,
            "matched_policy_name": str,
            "allowed_actions": List[str],
            "reason": str
        }
        """
        policies = await cls.get_active_policies(db)
        sev_upper = severity.upper()
        sev_rank = cls.SEVERITY_ORDER.get(sev_upper, 1)

        # Select highest-matching policy based on risk score and severity
        matched = None
        for pol in sorted(policies, key=lambda x: x["minimum_risk_score"], reverse=True):
            pol_sev_rank = cls.SEVERITY_ORDER.get(pol["minimum_severity"].upper(), 1)
            if risk_score >= pol["minimum_risk_score"] and sev_rank >= pol_sev_rank:
                matched = pol
                break

        if not matched:
            matched = DEFAULT_POLICIES[0]  # Fallback to LOW

        allowed_actions = matched.get("allowed_actions", [])
        requires_approval = matched.get("requires_approval", True)

        if not allowed_actions:
            return {
                "decision": "DENY_NO_AUTOMATION",
                "is_allowed": False,
                "requires_approval": False,
                "matched_policy_name": matched["name"],
                "allowed_actions": [],
                "cooldown_seconds": matched.get("cooldown_seconds", 300),
                "reason": f"Policy '{matched['name']}' prohibits automation for {sev_upper} severity (Risk: {risk_score:.1f})."
            }

        if requested_action:
            action_clean = requested_action.upper().strip()
            if action_clean not in allowed_actions:
                return {
                    "decision": "DENY_ACTION_UNSUPPORTED",
                    "is_allowed": False,
                    "requires_approval": False,
                    "matched_policy_name": matched["name"],
                    "allowed_actions": allowed_actions,
                    "cooldown_seconds": matched.get("cooldown_seconds", 300),
                    "reason": f"Action '{action_clean}' is not permitted by policy '{matched['name']}'. Allowed: {allowed_actions}."
                }

        decision = "REQUIRE_APPROVAL" if requires_approval else "ALLOW"
        return {
            "decision": decision,
            "is_allowed": True,
            "requires_approval": requires_approval,
            "matched_policy_name": matched["name"],
            "allowed_actions": allowed_actions,
            "cooldown_seconds": matched.get("cooldown_seconds", 300),
            "reason": f"Policy '{matched['name']}' matched for {sev_upper} incident (Risk: {risk_score:.1f}). Decision: {decision}."
        }
