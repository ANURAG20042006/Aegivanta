import os
import sys
import json
import hashlib
import joblib
import platform
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from ml.dataset.generator import CICIDS2017DataGenerator
from ml.dataset.preprocessor import CICIDS2017Preprocessor
from ml.models.model_selector import ModelSelectorSuite
from ml.schema.feature_schema import DEFAULT_FEATURE_SCHEMA


def get_git_commit_hash() -> str:
    try:
        import subprocess
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=3)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return "unknown-git-ref"


def run_training_pipeline(
    dataset_path: str = None,
    num_synthetic_samples: int = 1500,
    artifacts_dir: str = "ml/artifacts",
    n_splits: int = 5,
    random_seed: int = 42
) -> List[Dict[str, Any]]:
    """
    Leakage-Proof SentinelAI ML Training & Cross-Validation Pipeline:
    1. Loads dataset.
    2. Performs train_test_split FIRST to set aside untouched test set.
    3. Runs Leakage-Free Stratified K-Fold Cross-Validation on training split ONLY.
    4. Evaluates model selector suite and selects champion model.
    5. Evaluates untouched test set ONCE for final metric reporting.
    6. Exports serialized model artifacts & complete metadata JSON.
    """
    print("==========================================================")
    print("      SentinelAI Leakage-Free ML Training Engine         ")
    print("==========================================================")

    artifacts_path = Path(artifacts_dir)
    artifacts_path.mkdir(parents=True, exist_ok=True)

    # Step 1: Load or Generate Dataset
    if dataset_path and os.path.exists(dataset_path):
        print(f"--> Loading real dataset from: {dataset_path}")
        df = pd.read_csv(dataset_path)
        dataset_id = Path(dataset_path).name
    else:
        print(f"--> Generating synthetic dataset ({num_synthetic_samples} samples)...")
        df = CICIDS2017DataGenerator.generate_synthetic_dataset(num_samples=num_synthetic_samples)
        dataset_id = "synthetic_cicids2017_benchmark"

    df_hash = hashlib.sha256(df.to_csv().encode("utf-8")).hexdigest()[:16]
    print(f"--> Dataset Loaded. Shape: {df.shape}, Hash: {df_hash}")

    # Step 2: Fit-Transform with Strict Split-First Architecture
    print("--> Splitting train/test sets FIRST & fitting preprocessing ONLY on X_train...")
    preprocessor = CICIDS2017Preprocessor(n_features_to_select=30)
    X_train, X_test, y_train, y_test = preprocessor.fit_transform_train_test(
        df, target_column="Label", balance_data=True, test_size=0.20, random_state=random_seed
    )

    # Save Preprocessor Artifact
    preprocessor_path = artifacts_path / "preprocessor.joblib"
    joblib.dump(preprocessor, preprocessor_path)
    print(f"--> Preprocessor artifact saved to: {preprocessor_path}")

    # Step 3: Leakage-Free Stratified K-Fold Cross-Validation on X_train Folds
    print(f"--> Running Leakage-Free {n_splits}-Fold Stratified Cross-Validation on Training Split...")
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_seed)
    cv_scores = []
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
        X_tr_fold, X_val_fold = X_train[train_idx], X_train[val_idx]
        y_tr_fold, y_val_fold = y_train[train_idx], y_train[val_idx]
        
        # Fit benchmark Random Forest model per fold
        from sklearn.ensemble import RandomForestClassifier
        rf_fold = RandomForestClassifier(n_estimators=50, random_state=random_seed)
        rf_fold.fit(X_tr_fold, y_tr_fold)
        preds_fold = rf_fold.predict(X_val_fold)
        f1_fold = float(f1_score(y_val_fold, preds_fold, average="macro", zero_division=0))
        cv_scores.append(f1_fold)

    cv_mean = float(np.mean(cv_scores))
    cv_std = float(np.std(cv_scores))
    print(f"--> Cross-Validation Complete. Mean Macro F1: {cv_mean:.4f} ± {cv_std:.4f}")

    # Step 4: Train & Compare Model Selector Suite
    print("--> Training & comparing model selector suite...")
    selector = ModelSelectorSuite(artifacts_dir=artifacts_dir)
    results = selector.train_and_evaluate_all(X_train, y_train, X_test, y_test)

    # Step 5: Metadata Generation
    champion_name = selector.best_model.model_name if selector.best_model else "Random Forest"
    metadata = {
        "model_version": f"{champion_name.lower().replace(' ', '_')}-v1.0",
        "feature_schema_version": DEFAULT_FEATURE_SCHEMA.version,
        "dataset_identifier": dataset_id,
        "dataset_hash": df_hash,
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "random_seed": random_seed,
        "python_version": platform.python_version(),
        "library_versions": {
            "scikit-learn": pd.__name__,
            "numpy": np.__version__,
            "pandas": pd.__version__
        },
        "selected_features": preprocessor.selected_feature_names,
        "cv_metrics": {
            "n_splits": n_splits,
            "macro_f1_mean": round(cv_mean, 4),
            "macro_f1_std": round(cv_std, 4)
        },
        "leaderboard": [
            {
                "model_name": r["model_name"],
                "model_type": r["model_type"],
                "accuracy": r["accuracy"],
                "f1_score": r["f1_score"],
                "precision": r["precision"],
                "recall": r["recall"]
            }
            for r in results
        ],
        "preprocessing_version": "split_first_smote_train_only",
        "git_commit": get_git_commit_hash()
    }

    metadata_path = artifacts_path / "metadata.json"
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"--> Comprehensive metadata saved to: {metadata_path}")
    return results


if __name__ == "__main__":
    run_training_pipeline()
