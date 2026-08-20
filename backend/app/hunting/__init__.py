"""
backend/app/hunting/__init__.py
===============================
Phase 3.8 Modular Threat Hunting Rules Package.
"""

from backend.app.hunting.base import HuntRule
from backend.app.hunting.production_hunts import (
    HuntRuleRegistry, hunt_rule_registry,
    HuntRepeatedAuthFailureToSuccess,
    HuntNewSourcePrivilegedAccess,
    HuntUnusualLateralMovement,
    HuntHighVolumeOutboundExfil,
    HuntIOCSuspiciousAuthCombination,
    HuntMultiAssetAccountAccess,
    HuntRareDestinationConnection,
    HuntHighVelocityEventBurst,
    HuntSuspiciousAdminActivity,
    HuntMultiStageAttackSequence
)

__all__ = [
    "HuntRule",
    "HuntRuleRegistry",
    "hunt_rule_registry",
    "HuntRepeatedAuthFailureToSuccess",
    "HuntNewSourcePrivilegedAccess",
    "HuntUnusualLateralMovement",
    "HuntHighVolumeOutboundExfil",
    "HuntIOCSuspiciousAuthCombination",
    "HuntMultiAssetAccountAccess",
    "HuntRareDestinationConnection",
    "HuntHighVelocityEventBurst",
    "HuntSuspiciousAdminActivity",
    "HuntMultiStageAttackSequence"
]
