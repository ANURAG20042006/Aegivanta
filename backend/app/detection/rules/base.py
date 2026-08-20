"""
backend/app/detection/rules/base.py
===================================
Phase 3.6 Modular Detection Rule Framework.
Defines the abstract DetectionRule interface and execution contract.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class DetectionRule(ABC):
    """
    Abstract base class for all SentinelAI detection rules.
    Every rule must be deterministic, evidence-backed, and mapped to MITRE ATT&CK techniques.
    """

    rule_id: str = "RULE-000"
    name: str = "Base Detection Rule"
    description: str = "Abstract base rule definition"
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    mitre_techniques: List[str] = []

    @abstractmethod
    def evaluate(self, event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Evaluates a security event and optional temporal context.
        Returns a detection match dictionary if triggered, or None if benign.
        Match Dict format:
        {
            "rule_id": self.rule_id,
            "rule_name": self.name,
            "matched": True,
            "confidence": 0.0 - 1.0,
            "severity": self.severity,
            "mitre_techniques": self.mitre_techniques,
            "description": str,
            "evidence": Dict[str, Any]
        }
        """
        pass
