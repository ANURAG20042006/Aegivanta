"""
backend/app/services/response_actions/base.py
=============================================
Phase 3.7 Modular SOAR Response Action Base Interface.
Defines execution lifecycle methods: validate, preview, execute, verify, rollback.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple


class ResponseAction(ABC):
    """
    Abstract contract for all SentinelAI automated response actions.
    Enforces validation, dry-run simulation, execution, verification, and rollback.
    """

    action_type: str = "BASE_ACTION"
    is_reversible: bool = True

    @abstractmethod
    def validate(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        """
        Validates target syntax, safety constraints, and parameters.
        Returns: (is_valid, failure_reason)
        """
        pass

    @abstractmethod
    def preview(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generates safe dry-run preview simulation without executing real changes.
        """
        pass

    @abstractmethod
    async def execute(self, target: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes the response action through safe infrastructure adapters.
        Returns: {"status": "SUCCESS" | "FAILED" | "BLOCKED", "details": Dict, "reversal_state": Dict}
        """
        pass

    @abstractmethod
    async def verify(self, target: str, execution_result: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verifies that the remediation was actually applied to target infrastructure.
        Returns: (is_verified, verification_message)
        """
        pass

    @abstractmethod
    async def rollback(self, target: str, reversal_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restores target to prior state before execution.
        Returns: {"status": "ROLLED_BACK" | "FAILED" | "ROLLBACK_UNAVAILABLE", "details": Dict}
        """
        pass
