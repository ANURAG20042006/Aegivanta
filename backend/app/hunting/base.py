"""
backend/app/hunting/base.py
===========================
Phase 3.8 Abstract Base Threat Hunting Rule.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class HuntRule(ABC):
    """Abstract base class for modular threat hunting rules."""

    hunt_id: str = "HUNT-000"
    name: str = "Base Threat Hunt"
    description: str = ""
    severity: str = "MEDIUM"
    mitre_technique: str = "T1000"
    tactic: str = "TA0001"

    @abstractmethod
    def evaluate(self, telemetry_events: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Evaluates a collection of telemetry events against hunting rule hypotheses.
        Returns a list of matching findings with empirical evidence and confidence scores.
        """
        pass
