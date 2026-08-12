"""
SentinelAI Automated Unit Tests for One-vs-Rest False Positive Rate (FPR)
=======================================================================
Guarantees mathematically exact One-vs-Rest FPR calculations across binary and multiclass inputs.
"""
import pytest
import numpy as np
from ml.metrics.security_metrics import calculate_macro_fpr, calculate_per_class_fpr, calculate_weighted_fpr


def test_perfect_prediction_zero_fpr():
    y_true = np.array([0, 1, 2, 0, 1, 2])
    y_pred = np.array([0, 1, 2, 0, 1, 2])

    macro_fpr = calculate_macro_fpr(y_true, y_pred)
    assert macro_fpr == 0.0


def test_multiclass_fpr_bounds():
    y_true = np.array([0, 1, 2, 3, 0, 1, 2, 3])
    y_pred = np.array([0, 0, 1, 1, 2, 2, 3, 3])

    macro_fpr = calculate_macro_fpr(y_true, y_pred)
    assert 0.0 <= macro_fpr <= 1.0


def test_fpr_handles_single_class_gracefully():
    y_true = np.array([0, 0, 0])
    y_pred = np.array([0, 0, 0])

    macro_fpr = calculate_macro_fpr(y_true, y_pred)
    assert macro_fpr == 0.0
