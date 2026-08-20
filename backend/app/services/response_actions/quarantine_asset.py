"""
backend/app/services/response_actions/quarantine_asset.py
========================================================
Phase 3.7 Asset Quarantine Response Action.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from backend.app.services.response_actions.base import ResponseAction

logger = logging.getLogger("SentinelAI")


class AssetQuarantineAdapter:
    """Manages asset security zone segregation."""
    _quarantined_assets: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def quarantine_asset(cls, asset_id: str, reason: str = "Crown jewel threat quarantine") -> Dict[str, Any]:
        cls._quarantined_assets[asset_id] = {
            "asset_id": asset_id,
            "quarantined_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "security_zone": "RESTRICTED_DMZ"
        }
        logger.info("Asset quarantine adapter isolated asset: %s", asset_id)
        return cls._quarantined_assets[asset_id]

    @classmethod
    def restore_asset(cls, asset_id: str) -> bool:
        if asset_id in cls._quarantined_assets:
            del cls._quarantined_assets[asset_id]
            logger.info("Asset quarantine adapter restored asset: %s", asset_id)
            return True
        return False

    @classmethod
    def is_quarantined(cls, asset_id: str) -> bool:
        return asset_id in cls._quarantined_assets

    @classmethod
    def reset(cls):
        cls._quarantined_assets.clear()


class QuarantineAssetAction(ResponseAction):
    """Quarantine Protected Asset Action."""
    action_type = "QUARANTINE_ASSET"
    is_reversible = True

    VALID_ID_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.]{1,128}$")

    def validate(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        target_clean = target.strip()
        if not target_clean:
            return False, "Target asset identifier cannot be empty."
        if not self.VALID_ID_REGEX.match(target_clean):
            return False, f"Target asset identifier '{target}' contains invalid characters."
        return True, None

    def preview(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        is_valid, err = self.validate(target, parameters)
        return {
            "action_type": self.action_type,
            "target": target,
            "is_valid": is_valid,
            "validation_error": err,
            "would_execute": is_valid,
            "target_zone": "RESTRICTED_DMZ",
            "is_reversible": self.is_reversible
        }

    async def execute(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        is_valid, err = self.validate(target, parameters)
        if not is_valid:
            return {"status": "FAILED", "failure_reason": err, "details": {}, "reversal_state": {}}

        prior = AssetQuarantineAdapter.is_quarantined(target)
        q_data = AssetQuarantineAdapter.quarantine_asset(target, reason=(parameters or {}).get("reason", "Asset containment"))
        return {
            "status": "SUCCESS",
            "details": {
                "action": "QUARANTINE_ASSET",
                "target": target,
                "quarantined_at": q_data["quarantined_at"],
                "security_zone": q_data["security_zone"]
            },
            "reversal_state": {"previously_quarantined": prior, "target": target}
        }

    async def verify(self, target: str, execution_result: Dict[str, Any]) -> Tuple[bool, str]:
        if AssetQuarantineAdapter.is_quarantined(target):
            return True, f"Verified asset '{target}' is quarantined in RESTRICTED_DMZ."
        return False, f"Verification failed: Asset '{target}' not found in active quarantine table."

    async def rollback(self, target: str, reversal_state: Dict[str, Any]) -> Dict[str, Any]:
        if not reversal_state.get("previously_quarantined", False):
            restored = AssetQuarantineAdapter.restore_asset(target)
            return {"status": "ROLLED_BACK" if restored else "SUCCEEDED", "details": {"action": "RESTORE_ASSET", "target": target}}
        return {"status": "SUCCEEDED", "details": {"action": "MAINTAIN_QUARANTINE", "target": target}}
