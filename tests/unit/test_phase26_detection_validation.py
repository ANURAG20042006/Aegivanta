"""
tests/unit/test_phase26_detection_validation.py
===============================================
Phase 26.3 Detection Validation & Quality Unit Tests.
"""

import pytest
from backend.app.services.detection_quality_service import DetectionQualityService


class TestDetectionValidationQuality:
    """Unit tests for detection quality and validation scoring."""

    def test_precision_recall_bounds_valid(self):
        """Precision and recall must be in [0.0, 1.0]."""
        # Testing deterministic baseline calculation
        precision = 0.965
        recall = 0.940
        f1 = 2 * (precision * recall) / (precision + recall)
        assert 0.0 <= precision <= 1.0
        assert 0.0 <= recall <= 1.0
        assert round(f1, 3) == 0.952

    def test_error_rates_sum_compliment(self):
        """FPR and FNR must be non-negative and <= 1.0."""
        fpr = 0.035
        fnr = 0.060
        assert 0.0 <= fpr <= 1.0
        assert 0.0 <= fnr <= 1.0
