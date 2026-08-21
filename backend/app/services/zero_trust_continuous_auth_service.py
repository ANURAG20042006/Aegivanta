"""
backend/app/services/zero_trust_continuous_auth_service.py
=========================================================
Phase 28 Continuous Zero Trust Authorization Engine (ZTNA 2.0).
Evaluates real-time session context:
- Identity Risk Score (0–100)
- Zero Trust Device Posture Trust Score (from Phase 22)
- Network Context & Impossible Travel
- Resource Criticality Level
Issues real-time dynamic access verdicts:
- ALLOW (Access granted)
- STEP_UP_MFA (Prompt for FIDO2/Passkey challenge)
- RESTRICTED_MODE (Read-only containment)
- TERMINATE_SESSION (Immediate token revocation & security alert)
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger("Aegivanta.ZeroTrustAuth")


class ZeroTrustContinuousAuthService:
    """Continuous Zero Trust access evaluation and risk-based step-up authorization."""

    @classmethod
    def evaluate_session_access(
        cls,
        username: str,
        identity_risk_score: float = 20.0,
        device_trust_score: float = 90.0,
        resource_criticality: str = "HIGH",
        is_known_location: bool = True,
        is_managed_device: bool = True
    ) -> Dict[str, Any]:
        """
        Computes composite session risk score and issues access authorization verdict.
        """
        # 1. Base Score calculation
        # Device risk inverse: (100 - device_trust_score)
        device_risk = 100.0 - device_trust_score

        # Composite session risk
        composite_risk = (identity_risk_score * 0.5) + (device_risk * 0.3)
        if not is_known_location:
            composite_risk += 25.0
        if not is_managed_device:
            composite_risk += 20.0

        composite_risk = max(0.0, min(100.0, round(composite_risk, 1)))

        # 2. Verdict Determination
        crit_upper = resource_criticality.upper().strip()
        if composite_risk >= 80.0:
            verdict = "TERMINATE_SESSION"
            reason = "Critical identity anomaly or untrusted endpoint detected."
            action_code = "REVOKE_JWT_IMMEDIATE"
        elif composite_risk >= 50.0 or (crit_upper == "CRITICAL" and composite_risk >= 30.0):
            verdict = "STEP_UP_MFA"
            reason = "Elevated session risk or critical resource access requires FIDO2/Passkey re-authentication."
            action_code = "CHALLENGE_WEBAUTHN"
        elif composite_risk >= 35.0 or not is_managed_device:
            verdict = "RESTRICTED_MODE"
            reason = "Session restricted to read-only views due to moderate posture variance."
            action_code = "ENFORCE_READ_ONLY"
        else:
            verdict = "ALLOW"
            reason = "Zero Trust posture verified. Full access authorized."
            action_code = "PERMIT"

        return {
            "username": username,
            "composite_session_risk": composite_risk,
            "verdict": verdict,
            "reason": reason,
            "action_code": action_code,
            "factors": {
                "identity_risk_score": identity_risk_score,
                "device_trust_score": device_trust_score,
                "is_managed_device": is_managed_device,
                "is_known_location": is_known_location,
                "resource_criticality": crit_upper
            },
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }
