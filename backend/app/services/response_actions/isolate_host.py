"""
backend/app/services/response_actions/isolate_host.py
====================================================
Phase 3.7 Host Isolation Response Action & Endpoint Containment Adapter.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from backend.app.services.response_actions.base import ResponseAction

logger = logging.getLogger("SentinelAI")


class HostIsolationAdapter:
    """
    Host / Endpoint isolation adapter managing host network quarantine.
    """
    _isolated_hosts: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def isolate_host(cls, host_id: str, reason: str = "Automated threat containment") -> Dict[str, Any]:
        cls._isolated_hosts[host_id] = {
            "host_id": host_id,
            "isolated_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "containment_vlan": 999
        }
        logger.info("Host isolation adapter applied network quarantine to host: %s", host_id)
        return cls._isolated_hosts[host_id]

    @classmethod
    def release_host(cls, host_id: str) -> bool:
        if host_id in cls._isolated_hosts:
            del cls._isolated_hosts[host_id]
            logger.info("Host isolation adapter released quarantine for host: %s", host_id)
            return True
        return False

    @classmethod
    def is_isolated(cls, host_id: str) -> bool:
        return host_id in cls._isolated_hosts

    @classmethod
    def reset(cls):
        cls._isolated_hosts.clear()


class HostIsolationAction(ResponseAction):
    """Host / Workstation / Server Isolation Action."""
    action_type = "ISOLATE_HOST"
    is_reversible = True

    # Reject shell metacharacters or malformed identifiers
    VALID_HOST_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.]{1,128}$")

    def validate(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        target_clean = target.strip()
        if not target_clean:
            return False, "Target host identifier cannot be empty."
        if not self.VALID_HOST_REGEX.match(target_clean):
            return False, f"Target host identifier '{target}' contains invalid characters or injection attempts."
        return True, None

    def preview(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        is_valid, err = self.validate(target, parameters)
        return {
            "action_type": self.action_type,
            "target": target,
            "is_valid": is_valid,
            "validation_error": err,
            "would_execute": is_valid,
            "containment_mode": "NETWORK_ISOLATION_EXCEPT_SOC_MANAGEMENT",
            "is_reversible": self.is_reversible
        }

    async def execute(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        is_valid, err = self.validate(target, parameters)
        if not is_valid:
            return {
                "status": "FAILED",
                "failure_reason": err,
                "details": {},
                "reversal_state": {}
            }

        reason = (parameters or {}).get("reason", "SentinelAI lateral movement containment")
        prior_state = HostIsolationAdapter.is_isolated(target)
        iso_data = HostIsolationAdapter.isolate_host(target, reason=reason)

        return {
            "status": "SUCCESS",
            "details": {
                "action": "ISOLATE_HOST",
                "target": target,
                "isolated_at": iso_data["isolated_at"],
                "containment_vlan": iso_data["containment_vlan"]
            },
            "reversal_state": {
                "previously_isolated": prior_state,
                "target": target
            }
        }

    async def verify(self, target: str, execution_result: Dict[str, Any]) -> Tuple[bool, str]:
        if HostIsolationAdapter.is_isolated(target):
            return True, f"Verified host '{target}' is currently in network isolation quarantine."
        return False, f"Verification failed: Host '{target}' was not found in active isolation table."

    async def rollback(self, target: str, reversal_state: Dict[str, Any]) -> Dict[str, Any]:
        was_previously_isolated = reversal_state.get("previously_isolated", False)
        if not was_previously_isolated:
            released = HostIsolationAdapter.release_host(target)
            return {
                "status": "ROLLED_BACK" if released else "SUCCEEDED",
                "details": {"action": "RELEASE_HOST", "target": target, "restored": True}
            }
        return {
            "status": "SUCCEEDED",
            "details": {"action": "MAINTAIN_ISOLATION", "target": target, "reason": "Host was isolated prior to action."}
        }
