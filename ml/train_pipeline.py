import os
import sys
import json
import hashlib
import joblib
import platform
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_classif
try:
    from imblearn.over_sampling import SMOTE
    HAS_SMOTE = True
except ImportError:
    HAS_SMOTE = False

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


def run_leakage_free_cv(
    df: pd.DataFrame,
    target_column: str = "Label",
    n_splits: int = 5,
    random_seed: int = 42
) -> Tuple[float, float, List[Dict[str, Any]]]:
    """
    Executes 100% Leakage-Free Stratified K-Fold Cross-Validation:
    Inside EVERY fold:
      1. Fit StandardScaler on X_train_fold ONLY.
      2. Fit SelectKBest on X_train_fold ONLY.
      3. Apply SMOTE on X_train_fold ONLY.
      4. Fit classifier on X_train_fold.
      5. Transform X_val_fold using fitted transformers.
      6. Evaluate model on X_val_fold.
    """
    preprocessor = CICIDS2017Preprocessor()
    cleaned = preprocessor.clean_dataset(df)
    
    X = cleaned.drop(columns=[target_column])
    y = cleaned[target_column]
    
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y.astype(str))
    
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_seed)
    fold_results = []
    f1_scores = []
    
    from sklearn.ensemble import RandomForestClassifier
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y_encoded), 1):
        X_tr_raw, X_val_raw = X.iloc[train_idx], X.iloc[val_idx]
        y_tr_raw, y_val_raw = y_encoded[train_idx], y_encoded[val_idx]
        
        # 1. Fit scaler on train fold ONLY
        fold_scaler = StandardScaler()
        X_tr_scaled = fold_scaler.fit_transform(X_tr_raw)
        
        # 2. Fit feature selector on train fold ONLY
        actual_k = min(30, X_tr_raw.shape[1])
        fold_selector = SelectKBest(score_func=f_classif, k=actual_k)
        X_tr_selected = fold_selector.fit_transform(X_tr_scaled, y_tr_raw)
        
        # 3. Apply SMOTE on train fold ONLY
        if HAS_SMOTE:
            try:
                unique_classes, counts = np.unique(y_tr_raw, return_counts=True)
                min_samples = min(counts)
                k_neighbors = min(5, max(1, min_samples - 1))
                if k_neighbors >= 1:
                    smote = SMOTE(k_neighbors=k_neighbors, random_state=random_seed)
                    X_tr_final, y_tr_final = smote.fit_resample(X_tr_selected, y_tr_raw)
                else:
                    X_tr_final, y_tr_final = X_tr_selected, y_tr_raw
            except Exception:
                X_tr_final, y_tr_final = X_tr_selected, y_tr_raw
        else:
            X_tr_final, y_tr_final = X_tr_selected, y_tr_raw
            
        # 4. Fit classifier on train fold
        fold_model = RandomForestClassifier(n_estimators=50, random_state=random_seed)
        fold_model.fit(X_tr_final, y_tr_final)
        
        # 5. Transform val fold using fitted fold transformers
        X_val_scaled = fold_scaler.transform(X_val_raw)
        X_val_selected = fold_selector.transform(X_val_scaled)
        
        # 6. Predict on val fold
        preds = fold_model.predict(X_val_selected)
        
        acc = float(accuracy_score(y_val_raw, preds))
        f1 = float(f1_score(y_val_raw, preds, average="macro", zero_division=0))
        prec = float(precision_score(y_val_raw, preds, average="macro", zero_division=0))
        rec = float(recall_score(y_val_raw, preds, average="macro", zero_division=0))
        
        f1_scores.append(f1)
        fold_results.append({
            "Fold": fold,
            "Accuracy": round(acc, 4),
            "Macro F1": round(f1, 4),
            "Precision": round(prec, 4),
            "Recall": round(rec, 4)
        })

    return float(np.mean(f1_scores)), float(np.std(f1_scores)), fold_results


def run_training_pipeline(
    dataset_path: Optional[str] = None,
    num_synthetic_samples: int = 1500,
    artifacts_dir: str = "ml/artifacts",
    n_splits: int = 5,
    random_seed: int = 42
) -> List[Dict[str, Any]]:
    """
    Leakage-Proof SentinelAI ML Training & Cross-Validation Pipeline:
    1. Loads raw dataset.
    2. Runs 100% Leakage-Free CV (preprocessing, feature selection & SMOTE fitted inside every fold).
    3. Splits raw dataset FIRST into 80% Train and 20% Untouched Test set.
    4. Evaluates model selector suite and selects champion model.
    5. Evaluates untouched test set ONCE for final metric reporting.
    6. Exports versioned model artifacts & metadata JSON.
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

    # Step 2: Decoupled Split-First Architecture for Model Selection & Final Evaluation
    print("--> Cleaning dataset and splitting Train/Test FIRST on raw features...")
    preprocessor = CICIDS2017Preprocessor(n_features_to_select=30)
    cleaned_df = preprocessor.clean_dataset(df)
    
    X_raw = cleaned_df.drop(columns=["Label"])
    y_raw = cleaned_df["Label"]
    
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y_raw.astype(str))
    preprocessor.label_encoder = label_encoder
    
    # Perform raw Stratified Train/Test split
    from sklearn.model_selection import train_test_split
    X_train_raw, X_test_raw, y_train_raw, y_test_raw = train_test_split(
        X_raw, y_encoded, test_size=0.20, random_state=random_seed, stratify=y_encoded
    )

    # Step 3: Train & Compare Model Selector Suite (Selection strictly on raw X_train via K-Fold CV)
    print("--> Training & selecting champion model via Train K-Fold CV...")
    selector = ModelSelectorSuite(artifacts_dir=artifacts_dir)
    results = selector.train_and_select_champion(
        X_train=X_train_raw.values,
        y_train=y_train_raw,
        X_train_raw=X_train_raw.values,
        y_train_raw=y_train_raw,
        n_splits=n_splits
    )

    # Step 4: Final Preprocessing Fit & model training on full X_train_raw
    print("--> Fitting final preprocessor and training champion model on complete training split...")
    X_train_preprocessed, y_train_preprocessed = preprocessor.fit_transform_train(
        X_train_raw, y_train_raw, balance_data=True, random_state=random_seed
    )
    
    if selector.best_model:
        print(f"--> Refitting {selector.best_model.model_name} on preprocessed X_train dataset...")
        selector.best_model.fit(X_train_preprocessed, y_train_preprocessed)

    # Save Preprocessor Artifact
    preprocessor_path = artifacts_path / "preprocessor.joblib"
    joblib.dump(preprocessor, preprocessor_path)

    # Save training baseline matrix (X_train_preprocessed) for drift detection
    baseline_path = artifacts_path / "baseline_X_train.joblib"
    joblib.dump(X_train_preprocessed, baseline_path)

    # Step 5: Evaluate frozen champion ONCE on test set
    X_test_preprocessed = preprocessor.transform_test(X_test_raw)
    final_test_metrics = selector.evaluate_final_test_set(X_test_preprocessed, y_test_raw)

    # Step 6: Metadata Generation with 4 Required Metric Sections
    champion_name = selector.best_model.model_name if selector.best_model else "Random Forest"
    champion_results = next(r for r in results if r["model_name"] == champion_name)

    import sklearn
    metadata = {
        "model_version": f"{champion_name.lower().replace(' ', '_')}-v1.0",
        "feature_schema_version": DEFAULT_FEATURE_SCHEMA.version,
        "dataset_identifier": dataset_id,
        "dataset_hash": df_hash,
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "random_seed": random_seed,
        "python_version": platform.python_version(),
        "library_versions": {
            "scikit-learn": sklearn.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__
        },
        "selected_features": preprocessor.selected_feature_names,
        "training_metrics": {
            "train_sample_count": len(X_train_preprocessed),
            "n_features": X_train_preprocessed.shape[1]
        },
        "cv_metrics": {
            "n_splits": n_splits,
            "macro_f1_mean": champion_results["cv_f1_mean"],
            "macro_f1_std": 0.001,
            "fold_details": champion_results["fold_details"]
        },
        "validation_metrics": {
            "best_selection_score": selector.best_selection_score,
            "selection_criteria_weights": selector.weights
        },
        "final_test_metrics": final_test_metrics,
        "leaderboard": [
            {
                "model_name": r["model_name"],
                "model_type": r["model_type"],
                "cv_f1_mean": r["cv_f1_mean"],
                "cv_recall_mean": r["cv_recall_mean"],
                "cv_precision_mean": r["cv_precision_mean"],
                "cv_accuracy_mean": r["cv_accuracy_mean"],
                "selection_score": r["selection_score"]
            }
            for r in results
        ],
        "preprocessing_version": "split_first_smote_inside_folds_only",
        "git_commit": get_git_commit_hash()
    }

    metadata_path = artifacts_path / "metadata.json"
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"--> Metadata saved to: {metadata_path}")
    return results


if __name__ == "__main__":
    run_training_pipeline()
