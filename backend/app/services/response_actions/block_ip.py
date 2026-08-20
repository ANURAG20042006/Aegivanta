"""
backend/app/services/response_actions/block_ip.py
=================================================
Phase 3.7 Perimeter IP Blocking Response Action & Network Enforcement Adapter.
"""

import ipaddress
import logging
from typing import Dict, Any, Optional, Tuple, Set
from datetime import datetime, timezone

from backend.app.services.response_actions.base import ResponseAction

logger = logging.getLogger("SentinelAI")


class NetworkEnforcementAdapter:
    """
    Network perimeter firewall enforcement adapter.
    Maintains active perimeter blocklist and enforces safe rule manipulation.
    """
    _active_blocks: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def block_ip(cls, ip: str, duration_seconds: int = 3600, reason: str = "Automated threat block") -> Dict[str, Any]:
        cls._active_blocks[ip] = {
            "ip": ip,
            "blocked_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": duration_seconds,
            "reason": reason,
            "rule_id": f"FW-RULE-{abs(hash(ip)) % 1000000:06d}"
        }
        logger.info("Firewall adapter added drop rule for IP: %s (Rule ID: %s)", ip, cls._active_blocks[ip]["rule_id"])
        return cls._active_blocks[ip]

    @classmethod
    def unblock_ip(cls, ip: str) -> bool:
        if ip in cls._active_blocks:
            del cls._active_blocks[ip]
            logger.info("Firewall adapter removed drop rule for IP: %s", ip)
            return True
        return False

    @classmethod
    def is_blocked(cls, ip: str) -> bool:
        return ip in cls._active_blocks

    @classmethod
    def reset(cls):
        cls._active_blocks.clear()


class BlockIPAction(ResponseAction):
    """Safe Perimeter IP Blocking Action."""
    action_type = "BLOCK_IP"
    is_reversible = True

    FORBIDDEN_SUBNETS = [
        ipaddress.ip_network("127.0.0.0/8"),
        ipaddress.ip_network("0.0.0.0/8"),
        ipaddress.ip_network("255.255.255.255/32")
    ]

    def validate(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        try:
            ip = ipaddress.ip_address(target.strip())
            for forbidden in self.FORBIDDEN_SUBNETS:
                if ip in forbidden:
                    return False, f"Target IP '{target}' is a restricted system address and cannot be blocked."
            return True, None
        except ValueError:
            return False, f"Target '{target}' is not a valid IPv4 or IPv6 address format."

    def preview(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        is_valid, err = self.validate(target, parameters)
        return {
            "action_type": self.action_type,
            "target": target,
            "is_valid": is_valid,
            "validation_error": err,
            "would_execute": is_valid,
            "duration_seconds": (parameters or {}).get("duration_seconds", 3600),
            "simulated_rule": f"IPTABLES_DROP_SRC_{target}",
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

        duration = (parameters or {}).get("duration_seconds", 3600)
        reason = (parameters or {}).get("reason", "SentinelAI automated threat containment")

        prior_blocked = NetworkEnforcementAdapter.is_blocked(target)
        rule_data = NetworkEnforcementAdapter.block_ip(target, duration_seconds=duration, reason=reason)

        return {
            "status": "SUCCESS",
            "details": {
                "action": "BLOCK_IP",
                "target": target,
                "rule_id": rule_data["rule_id"],
                "duration_seconds": duration,
                "blocked_at": rule_data["blocked_at"]
            },
            "reversal_state": {
                "previously_blocked": prior_blocked,
                "target": target
            }
        }

    async def verify(self, target: str, execution_result: Dict[str, Any]) -> Tuple[bool, str]:
        if NetworkEnforcementAdapter.is_blocked(target):
            return True, f"Verified perimeter drop rule active for IP {target}."
        return False, f"Verification failed: Drop rule for IP {target} was not detected in active table."

    async def rollback(self, target: str, reversal_state: Dict[str, Any]) -> Dict[str, Any]:
        was_previously_blocked = reversal_state.get("previously_blocked", False)
        if not was_previously_blocked:
            unblocked = NetworkEnforcementAdapter.unblock_ip(target)
            return {
                "status": "ROLLED_BACK" if unblocked else "SUCCEEDED",
                "details": {"action": "UNBLOCK_IP", "target": target, "restored": True}
            }
        return {
            "status": "SUCCEEDED",
            "details": {"action": "MAINTAIN_BLOCK", "target": target, "reason": "Target was blocked prior to action."}
        }
