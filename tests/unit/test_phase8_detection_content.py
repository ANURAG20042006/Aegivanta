"""
tests/unit/test_phase8_detection_content.py
===========================================
Unit tests for Detection-as-Code Rule DSL, AST Evaluation, and Sandbox Testing.
"""

import pytest
from backend.app.services.detection_content_service import DetectionContentService


def test_evaluate_rule_dsl_simple():
    """Evaluates field equality and comparison operators."""
    event = {
        "event_type": "NETWORK_FLOW",
        "data": {
            "protocol": "TCP",
            "bytes": 5000,
            "src_ip": "10.0.0.5"
        }
    }

    # Equality check
    dsl_eq = {"field": "data.protocol", "op": "eq", "value": "TCP"}
    assert DetectionContentService.evaluate_rule_dsl(dsl_eq, event) is True

    # Greater than check
    dsl_gt = {"field": "data.bytes", "op": "gt", "value": 1000}
    assert DetectionContentService.evaluate_rule_dsl(dsl_gt, event) is True

    # Negative check
    dsl_neg = {"field": "data.bytes", "op": "lt", "value": 100}
    assert DetectionContentService.evaluate_rule_dsl(dsl_neg, event) is False


def test_evaluate_rule_dsl_logical_and_or():
    """Evaluates compound boolean AND/OR rule expressions."""
    event = {
        "data": {
            "user": "root",
            "src_ip": "192.168.1.100",
            "failed_attempts": 6
        }
    }

    compound_and = {
        "and": [
            {"field": "data.user", "op": "eq", "value": "root"},
            {"field": "data.failed_attempts", "op": "gt", "value": 5}
        ]
    }
    assert DetectionContentService.evaluate_rule_dsl(compound_and, event) is True

    compound_or = {
        "or": [
            {"field": "data.user", "op": "eq", "value": "guest"},
            {"field": "data.failed_attempts", "op": "gt", "value": 5}
        ]
    }
    assert DetectionContentService.evaluate_rule_dsl(compound_or, event) is True


def test_validate_rule_syntax():
    """Validates structural constraints of Detection-as-Code definitions."""
    valid_payload = {
        "rule_code": "AEG-R-2026-001",
        "name": "Brute Force Attack Detector",
        "rule_dsl": {"field": "failed_count", "op": "gt", "value": 10}
    }
    is_valid, err = DetectionContentService.validate_rule(valid_payload)
    assert is_valid is True
    assert err is None

    invalid_payload = {"name": "Incomplete Rule"}
    is_valid_inv, err_inv = DetectionContentService.validate_rule(invalid_payload)
    assert is_valid_inv is False
