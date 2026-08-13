"""
SentinelAI Authoritative Security & Machine Learning Metrics Module
===================================================================
Single authoritative source of truth for:
  - Binary and Multiclass One-vs-Rest False Positive Rate (FPR)
  - Macro and Weighted FPR calculation
  - Macro F1, Precision, Recall, and Accuracy metrics

Formula:
  FPR_k = FP_k / (FP_k + TN_k)
  Macro FPR = mean(FPR_k across all classes)
"""
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score


def calculate_per_class_fpr(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Calculates One-vs-Rest False Positive Rate per target class."""
    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()
    
    classes = np.unique(np.concatenate([y_true, y_pred]))
    if len(classes) <= 1:
        return np.array([0.0])

    cm = confusion_matrix(y_true, y_pred, labels=classes)
    fp = cm.sum(axis=0) - np.diag(cm)
    fn = cm.sum(axis=1) - np.diag(cm)
    tp = np.diag(cm)
    tn = cm.sum() - (fp + fn + tp)

    denominator = fp + tn
    with np.errstate(divide='ignore', invalid='ignore'):
        class_fpr = np.where(denominator > 0, fp / denominator, 0.0)
    return class_fpr


def calculate_macro_fpr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates unweighted mean One-vs-Rest False Positive Rate across all classes."""
    class_fpr = calculate_per_class_fpr(y_true, y_pred)
    return float(np.mean(class_fpr))


def calculate_weighted_fpr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates class-prevalence weighted One-vs-Rest False Positive Rate."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    classes, counts = np.unique(y_true, return_counts=True)
    if len(classes) <= 1:
        return 0.0

    class_fpr = calculate_per_class_fpr(y_true, y_pred)
    weights = counts / counts.sum()
    if len(class_fpr) == len(weights):
        return float(np.sum(class_fpr * weights))
    return calculate_macro_fpr(y_true, y_pred)


def calculate_fpr(y_true: np.ndarray, y_pred: np.ndarray, mode: str = "macro") -> float:
    """Primary entry point for False Positive Rate calculation (mode: 'macro' or 'weighted')."""
    if mode == "weighted":
        return calculate_weighted_fpr(y_true, y_pred)
    return calculate_macro_fpr(y_true, y_pred)


def compute_per_class_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: Optional[List[str]] = None
) -> Dict[str, Dict[str, float]]:
    """
    Calculates per-class precision, recall, f1, and One-vs-Rest FPR.
    Returns dict mapping class_name -> {"precision": float, "recall": float, "f1": float, "fpr": float}.
    Uses actual sklearn metrics with average=None.
    """
    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()

    unique_labels = np.unique(np.concatenate([y_true, y_pred]))
    unique_labels.sort()

    prec_array = precision_score(y_true, y_pred, labels=unique_labels, average=None, zero_division=0)
    rec_array = recall_score(y_true, y_pred, labels=unique_labels, average=None, zero_division=0)
    f1_array = f1_score(y_true, y_pred, labels=unique_labels, average=None, zero_division=0)
    fpr_array = calculate_per_class_fpr(y_true, y_pred)

    per_class = {}
    for idx, lbl in enumerate(unique_labels):
        if class_names and idx < len(class_names):
            name = str(class_names[idx])
        elif class_names and isinstance(lbl, (int, np.integer)) and 0 <= int(lbl) < len(class_names):
            name = str(class_names[int(lbl)])
        else:
            name = str(lbl)

        per_class[name] = {
            "precision": round(float(prec_array[idx]), 4),
            "recall": round(float(rec_array[idx]), 4),
            "f1": round(float(f1_array[idx]), 4),
            "fpr": round(float(fpr_array[idx] if idx < len(fpr_array) else 0.0), 4)
        }
    return per_class


def compute_all_security_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Computes a comprehensive dictionary of all standardized evaluation metrics including per_class_metrics."""
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "macro_f1": round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "precision": round(float(precision_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        "fpr": round(calculate_macro_fpr(y_true, y_pred), 4),
        "weighted_fpr": round(calculate_weighted_fpr(y_true, y_pred), 4),
        "per_class_metrics": compute_per_class_metrics(y_true, y_pred, class_names=class_names)
    }

