"""
backend/app/services/response_actions/revoke_session.py
======================================================
Phase 3.7 Session Revocation Response Action.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from backend.app.services.response_actions.base import ResponseAction

logger = logging.getLogger("SentinelAI")


class AccountResponseAdapter:
    """Manages session invalidation and account state locks."""
    _revoked_sessions: Dict[str, Dict[str, Any]] = {}
    _disabled_accounts: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def revoke_user_sessions(cls, user_id: str, reason: str = "Credential compromise containment") -> Dict[str, Any]:
        cls._revoked_sessions[user_id] = {
            "user_id": user_id,
            "revoked_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason
        }
        logger.info("Account adapter revoked all active sessions for user: %s", user_id)
        return cls._revoked_sessions[user_id]

    @classmethod
    def is_session_revoked(cls, user_id: str) -> bool:
        return user_id in cls._revoked_sessions

    @classmethod
    def restore_sessions(cls, user_id: str) -> bool:
        if user_id in cls._revoked_sessions:
            del cls._revoked_sessions[user_id]
            return True
        return False

    @classmethod
    def disable_account(cls, user_id: str, reason: str = "Credential compromise") -> Dict[str, Any]:
        cls._disabled_accounts[user_id] = {
            "user_id": user_id,
            "disabled_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason
        }
        logger.info("Account adapter locked account for user: %s", user_id)
        return cls._disabled_accounts[user_id]

    @classmethod
    def enable_account(cls, user_id: str) -> bool:
        if user_id in cls._disabled_accounts:
            del cls._disabled_accounts[user_id]
            logger.info("Account adapter unlocked account for user: %s", user_id)
            return True
        return False

    @classmethod
    def is_account_disabled(cls, user_id: str) -> bool:
        return user_id in cls._disabled_accounts

    @classmethod
    def reset(cls):
        cls._revoked_sessions.clear()
        cls._disabled_accounts.clear()


class RevokeSessionAction(ResponseAction):
    """Revoke User Sessions Action."""
    action_type = "REVOKE_SESSION"
    is_reversible = True

    VALID_USER_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.@]{1,128}$")

    def validate(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        target_clean = target.strip()
        if not target_clean:
            return False, "Target user identifier cannot be empty."
        if not self.VALID_USER_REGEX.match(target_clean):
            return False, f"Target user '{target}' contains invalid characters."
        return True, None

    def preview(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        is_valid, err = self.validate(target, parameters)
        return {
            "action_type": self.action_type,
            "target": target,
            "is_valid": is_valid,
            "validation_error": err,
            "would_execute": is_valid,
            "is_reversible": self.is_reversible
        }

    async def execute(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        is_valid, err = self.validate(target, parameters)
        if not is_valid:
            return {"status": "FAILED", "failure_reason": err, "details": {}, "reversal_state": {}}

        prior = AccountResponseAdapter.is_session_revoked(target)
        rev_data = AccountResponseAdapter.revoke_user_sessions(target, reason=(parameters or {}).get("reason", "Session revocation"))
        return {
            "status": "SUCCESS",
            "details": {
                "action": "REVOKE_SESSION",
                "target": target,
                "revoked_at": rev_data["revoked_at"]
            },
            "reversal_state": {"previously_revoked": prior, "target": target}
        }

    async def verify(self, target: str, execution_result: Dict[str, Any]) -> Tuple[bool, str]:
        if AccountResponseAdapter.is_session_revoked(target):
            return True, f"Verified active sessions for user '{target}' are revoked."
        return False, f"Verification failed: User '{target}' was not marked revoked in auth cache."

    async def rollback(self, target: str, reversal_state: Dict[str, Any]) -> Dict[str, Any]:
        if not reversal_state.get("previously_revoked", False):
            restored = AccountResponseAdapter.restore_sessions(target)
            return {"status": "ROLLED_BACK" if restored else "SUCCEEDED", "details": {"action": "RESTORE_SESSION", "target": target}}
        return {"status": "SUCCEEDED", "details": {"action": "MAINTAIN_REVOCATION", "target": target}}
