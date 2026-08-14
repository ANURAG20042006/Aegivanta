"""
SentinelAI Authoritative Model Artifact Mapping Registry
=========================================================
Single Source of Truth for model name to artifact filename, artifact path,
and framework type ("joblib" vs "pytorch").
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

# Authoritative specification mapping display names to canonical filenames and framework types
MODEL_ARTIFACT_SPECS: Dict[str, Dict[str, str]] = {
    "Random Forest":      {"filename": "random_forest.joblib",      "type": "joblib"},
    "XGBoost":            {"filename": "xgboost.joblib",            "type": "joblib"},
    "LightGBM":           {"filename": "lightgbm.joblib",           "type": "joblib"},
    "CatBoost":           {"filename": "catboost.joblib",           "type": "joblib"},
    "Decision Tree":      {"filename": "decision_tree.joblib",      "type": "joblib"},
    "Logistic Regression": {"filename": "logistic_regression.joblib", "type": "joblib"},
    "SVM":                {"filename": "svm.joblib",                "type": "joblib"},
    "KNN":                {"filename": "knn.joblib",                "type": "joblib"},
    "Naive Bayes":        {"filename": "naive_bayes.joblib",        "type": "joblib"},
    "1D-CNN":             {"filename": "cnn_1d.pt",                 "type": "pytorch"},
    "LSTM":               {"filename": "lstm.pt",                   "type": "pytorch"},
    "Autoencoder":        {"filename": "autoencoder.pt",            "type": "pytorch"},
}

PYTORCH_MODEL_NAMES = {"1D-CNN", "LSTM", "Autoencoder"}


def get_artifact_spec(model_name: str) -> Dict[str, str]:
    """Returns canonical artifact filename and framework type for a given model_name."""
    if model_name in MODEL_ARTIFACT_SPECS:
        return MODEL_ARTIFACT_SPECS[model_name]
    
    # Check normalized prefixes (e.g. 'XGBoost v2.1' -> 'XGBoost')
    clean_name = model_name.split(" v")[0].split(" V")[0].strip()
    if clean_name in MODEL_ARTIFACT_SPECS:
        return MODEL_ARTIFACT_SPECS[clean_name]
    for k, v in MODEL_ARTIFACT_SPECS.items():
        if k.lower() == clean_name.lower():
            return v
    for k, v in MODEL_ARTIFACT_SPECS.items():
        if k.lower() in model_name.lower():
            return v

    # Fallback heuristic if an unlisted model name is passed
    slug = clean_name.lower().replace(" ", "_")
    if clean_name in PYTORCH_MODEL_NAMES or "cnn" in slug or "lstm" in slug or "autoencoder" in slug:
        return {"filename": f"{slug}.pt", "type": "pytorch"}
    return {"filename": f"{slug}.joblib", "type": "joblib"}


def resolve_model_artifact_path(
    model_name: str,
    artifacts_dir: Optional[Path] = None
) -> Tuple[Path, str, Optional[str], bool]:
    """
    Resolves exact artifact Path, framework type ("joblib"|"pytorch"),
    calculated SHA256 checksum, and file existence status.

    Returns:
        (relative_or_resolved_path, artifact_type, actual_sha256, exists)
    """
    if artifacts_dir is None:
        artifacts_dir = Path("ml/artifacts")

    spec = get_artifact_spec(model_name)
    target_path = artifacts_dir / spec["filename"]
    art_type = spec["type"]

    # Strict resolution: exact canonical artifact ONLY. No silent cross-model fallback.
    exists = target_path.exists() and target_path.is_file()
    actual_sha256 = None
    if exists:
        try:
            actual_sha256 = hashlib.sha256(target_path.read_bytes()).hexdigest()
        except Exception:
            actual_sha256 = None

    return target_path, art_type, actual_sha256, exists
