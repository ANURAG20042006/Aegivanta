"""
backend/app/detection/rules/__init__.py
"""
from backend.app.detection.rules.base import DetectionRule
from backend.app.detection.rules.production_rules import detection_registry, DetectionRuleRegistry

__all__ = ["DetectionRule", "detection_registry", "DetectionRuleRegistry"]
