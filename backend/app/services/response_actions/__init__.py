"""
backend/app/services/response_actions/__init__.py
=================================================
Phase 3.7 Response Action Registry.
"""

from typing import Dict, List, Optional
from backend.app.services.response_actions.base import ResponseAction
from backend.app.services.response_actions.block_ip import BlockIPAction, NetworkEnforcementAdapter
from backend.app.services.response_actions.isolate_host import HostIsolationAction, HostIsolationAdapter
from backend.app.services.response_actions.quarantine_asset import QuarantineAssetAction, AssetQuarantineAdapter
from backend.app.services.response_actions.revoke_session import RevokeSessionAction, AccountResponseAdapter
from backend.app.services.response_actions.disable_account import DisableAccountAction
from backend.app.services.response_actions.rollback import ResponseRollbackService


class ResponseActionRegistry:
    """Registry maintaining active modular SOAR response actions."""

    def __init__(self):
        self._actions: Dict[str, ResponseAction] = {
            "BLOCK_IP": BlockIPAction(),
            "ISOLATE_HOST": HostIsolationAction(),
            "QUARANTINE_ASSET": QuarantineAssetAction(),
            "REVOKE_SESSION": RevokeSessionAction(),
            "DISABLE_ACCOUNT": DisableAccountAction()
        }

    def get_action(self, action_type: str) -> Optional[ResponseAction]:
        return self._actions.get(action_type.upper().strip())

    def get_all_actions(self) -> List[str]:
        return list(self._actions.keys())


response_action_registry = ResponseActionRegistry()

__all__ = [
    "ResponseAction",
    "BlockIPAction",
    "HostIsolationAction",
    "QuarantineAssetAction",
    "RevokeSessionAction",
    "DisableAccountAction",
    "ResponseRollbackService",
    "NetworkEnforcementAdapter",
    "HostIsolationAdapter",
    "AssetQuarantineAdapter",
    "AccountResponseAdapter",
    "ResponseActionRegistry",
    "response_action_registry"
]
