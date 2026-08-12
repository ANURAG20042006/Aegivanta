"""
SentinelAI Automated Unit Tests for Authoritative Security Metrics Module
========================================================================
Validates accuracy, precision, recall, macro F1, and FPR metrics calculations.
"""
import pytest
import numpy as np
from ml.metrics.security_metrics import (
    calculate_per_class_fpr,
    calculate_macro_fpr,
    calculate_weighted_fpr,
    calculate_fpr,
    compute_all_security_metrics
)


def test_calculate_per_class_fpr_binary():
    # 2x2 confusion matrix: TP=8, FP=2, FN=1, TN=89
    y_true = np.array([1]*9 + [0]*91)
    y_pred = np.array([1]*8 + [0]*1 + [1]*2 + [0]*89)

    class_fprs = calculate_per_class_fpr(y_true, y_pred)
    assert len(class_fprs) == 2
    # Class 0: FP_0 = 1, TN_0 = 8 -> FPR_0 = 1/9 = 0.11111
    # Class 1: FP_1 = 2, TN_1 = 89 -> FPR_1 = 2/91 = 0.02197
    assert abs(class_fprs[0] - (1.0 / 9.0)) < 1e-4
    assert abs(class_fprs[1] - (2.0 / 91.0)) < 1e-4


def test_calculate_macro_fpr():
    y_true = np.array([1]*9 + [0]*91)
    y_pred = np.array([1]*8 + [0]*1 + [1]*2 + [0]*89)

    macro_fpr = calculate_macro_fpr(y_true, y_pred)
    expected = ( (1.0 / 9.0) + (2.0 / 91.0) ) / 2.0
    assert abs(macro_fpr - expected) < 1e-4


def test_calculate_weighted_fpr():
    y_true = np.array([1]*9 + [0]*91)
    y_pred = np.array([1]*8 + [0]*1 + [1]*2 + [0]*89)

    weighted_fpr = calculate_weighted_fpr(y_true, y_pred)
    # Weights: class 0 = 91/100, class 1 = 9/100
    expected = (1.0 / 9.0) * 0.91 + (2.0 / 91.0) * 0.09
    assert abs(weighted_fpr - expected) < 1e-4


def test_compute_all_security_metrics_keys():
    y_true = np.array([0, 1, 0, 1, 0, 1])
    y_pred = np.array([0, 1, 0, 0, 0, 1])

    metrics = compute_all_security_metrics(y_true, y_pred)
    for key in ["accuracy", "macro_f1", "precision", "recall", "fpr", "weighted_fpr"]:
        assert key in metrics
        assert isinstance(metrics[key], float)
