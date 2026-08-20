"""
backend/app/services/response_actions/disable_account.py
=======================================================
Phase 3.7 Account Lockdown Response Action.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from backend.app.services.response_actions.base import ResponseAction
from backend.app.services.response_actions.revoke_session import AccountResponseAdapter

logger = logging.getLogger("SentinelAI")


class DisableAccountAction(ResponseAction):
    """Disable/Lock User Account Action."""
    action_type = "DISABLE_ACCOUNT"
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

        prior = AccountResponseAdapter.is_account_disabled(target)
        lock_data = AccountResponseAdapter.disable_account(target, reason=(parameters or {}).get("reason", "Account lock"))
        return {
            "status": "SUCCESS",
            "details": {
                "action": "DISABLE_ACCOUNT",
                "target": target,
                "disabled_at": lock_data["disabled_at"]
            },
            "reversal_state": {"previously_disabled": prior, "target": target}
        }

    async def verify(self, target: str, execution_result: Dict[str, Any]) -> Tuple[bool, str]:
        if AccountResponseAdapter.is_account_disabled(target):
            return True, f"Verified account for user '{target}' is disabled/locked."
        return False, f"Verification failed: User '{target}' is not marked disabled in account adapter."

    async def rollback(self, target: str, reversal_state: Dict[str, Any]) -> Dict[str, Any]:
        if not reversal_state.get("previously_disabled", False):
            restored = AccountResponseAdapter.enable_account(target)
            return {"status": "ROLLED_BACK" if restored else "SUCCEEDED", "details": {"action": "ENABLE_ACCOUNT", "target": target}}
        return {"status": "SUCCEEDED", "details": {"action": "MAINTAIN_DISABLED", "target": target}}
