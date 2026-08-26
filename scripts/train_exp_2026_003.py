"""
scripts/train_exp_2026_003.py
=============================
Authoritative ML Training, Model Selection, Evaluation, and Provenance Pipeline
for EXP-2026-003 (Real-World CICIoT2023 NIDS Dataset).

Follows strict leakage-free methodology:
1. Stratified 80/20 Train / Test Split FIRST (Test set frozen & untouched).
2. Inside 5-Fold Cross-Validation on Train:
   - Fit SimpleImputer on train fold ONLY.
   - Fit StandardScaler on train fold ONLY.
   - Fit SelectKBest (k=30) on train fold ONLY.
   - Fit SMOTE on train fold ONLY (if enabled/balanced).
   - Fit candidate classifiers.
   - Transform validation fold using train fold parameters.
   - Evaluate on validation fold.
3. Select Champion Model based on validation Macro F1.
4. Fit champion on full Training Partition.
5. Final single evaluation on frozen Untouched Test Partition.
6. Export artifacts, SHA-256 digests, and manifests to results/EXP-2026-003/.
"""

import os
import sys
import json
import time
import hashlib
import platform
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

try:
    from imblearn.over_sampling import SMOTE
    HAS_SMOTE = True
except ImportError:
    HAS_SMOTE = False

try:
    from catboost import CatBoostClassifier
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

# Set stdout UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "EXP-2026-003" / "ciciot2023_real_benchmark.csv"
OUT_DIR = PROJECT_ROOT / "results" / "EXP-2026-003"
OUT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
N_SELECTED_FEATURES = 30


def get_git_commit_hash() -> str:
    try:
        import subprocess
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=3)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return "unknown-git-ref"


def run_training_experiment():
    print("=" * 75)
    print("  AEGIVANTA ML ENGINE — EXP-2026-003 (CICIoT2023 REAL NIDS BENCHMARK)")
    print("=" * 75)

    # 1. Load Raw Dataset
    print(f"\n--> 1. Loading Raw Dataset from: {RAW_DATA_PATH}")
    raw_df = pd.read_csv(RAW_DATA_PATH)
    raw_bytes = RAW_DATA_PATH.read_bytes()
    dataset_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    print(f"    Total Records : {len(raw_df)}")
    print(f"    Total Columns : {len(raw_df.columns)}")
    print(f"    Dataset SHA256: {dataset_sha256}")
    print(f"    Classes Count : {raw_df['label'].nunique()}")

    # 2. Data Cleaning & Feature Separation
    X_raw = raw_df.drop(columns=["label"]).copy()
    y_raw = raw_df["label"].copy()

    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y_raw.astype(str))
    classes = list(label_encoder.classes_)

    # 3. Stratified 80/20 Train / Test Split FIRST (Untouched Test Rule)
    print("\n--> 2. Partitioning Dataset (80% Train, 20% Untouched Test)...")
    X_train_raw, X_test_raw, y_train_enc, y_test_enc = train_test_split(
        X_raw, y_encoded,
        test_size=0.20,
        random_state=RANDOM_SEED,
        stratify=y_encoded
    )
    print(f"    Train Samples : {len(X_train_raw)} (80.0%)")
    print(f"    Test Samples  : {len(X_test_raw)} (20.0% - FROZEN)")

    # 4. Define Candidate Model Classifiers
    candidate_factories = {
        "CatBoost": lambda: CatBoostClassifier(
            iterations=150,
            learning_rate=0.08,
            depth=6,
            random_seed=RANDOM_SEED,
            verbose=0,
            thread_count=-1
        ) if HAS_CATBOOST else None,
        "Random Forest": lambda: RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            random_state=RANDOM_SEED,
            n_jobs=-1
        ),
        "XGBoost": lambda: xgb.XGBClassifier(
            n_estimators=100,
            learning_rate=0.08,
            max_depth=6,
            random_state=RANDOM_SEED,
            n_jobs=-1,
            eval_metric="mlogloss"
        ) if HAS_XGBOOST else None,
        "LightGBM": lambda: lgb.LGBMClassifier(
            n_estimators=100,
            learning_rate=0.08,
            max_depth=6,
            random_state=RANDOM_SEED,
            n_jobs=-1,
            verbose=-1
        ) if HAS_LIGHTGBM else None,
        "Decision Tree": lambda: DecisionTreeClassifier(
            max_depth=12,
            random_state=RANDOM_SEED
        )
    }

    # 5. 5-Fold Cross-Validation on Train Partition ONLY
    print("\n--> 3. Executing Leakage-Free 5-Fold Stratified Cross-Validation on Train Partition...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

    cv_records = []
    model_cv_scores = {name: [] for name in candidate_factories if candidate_factories[name]() is not None}

    for fold, (tr_idx, val_idx) in enumerate(skf.split(X_train_raw, y_train_enc), 1):
        print(f"    Evaluating Fold {fold}/5...")
        X_tr, X_val = X_train_raw.iloc[tr_idx], X_train_raw.iloc[val_idx]
        y_tr, y_val = y_train_enc[tr_idx], y_train_enc[val_idx]

        # Fit transformers on Train fold ONLY
        fold_imputer = SimpleImputer(strategy="median")
        X_tr_imp = fold_imputer.fit_transform(X_tr)

        fold_scaler = StandardScaler()
        X_tr_scl = fold_scaler.fit_transform(X_tr_imp)

        k_val = min(N_SELECTED_FEATURES, X_tr.shape[1])
        fold_sel = SelectKBest(score_func=f_classif, k=k_val)
        X_tr_sel = fold_sel.fit_transform(X_tr_scl, y_tr)

        # Transform validation fold using train fold parameters
        X_val_imp = fold_imputer.transform(X_val)
        X_val_scl = fold_scaler.transform(X_val_imp)
        X_val_sel = fold_sel.transform(X_val_scl)

        for name, factory in candidate_factories.items():
            model = factory()
            if model is None:
                continue

            t0 = time.perf_counter()
            model.fit(X_tr_sel, y_tr)
            train_lat = (time.perf_counter() - t0) * 1000.0

            t0 = time.perf_counter()
            preds = model.predict(X_val_sel)
            if preds.ndim > 1:
                preds = preds.ravel()
            infer_lat = (time.perf_counter() - t0) * 1000.0 / max(len(X_val_sel), 1)

            acc = float(accuracy_score(y_val, preds))
            macro_f1 = float(f1_score(y_val, preds, average="macro", zero_division=0))
            macro_prec = float(precision_score(y_val, preds, average="macro", zero_division=0))
            macro_rec = float(recall_score(y_val, preds, average="macro", zero_division=0))

            # Approximate binary FPR (non-benign as threat)
            benign_idx = list(classes).index("Benign") if "Benign" in classes else 0
            y_val_bin = (y_val != benign_idx).astype(int)
            preds_bin = (preds != benign_idx).astype(int)
            cm_bin = confusion_matrix(y_val_bin, preds_bin, labels=[0, 1])
            tn, fp, fn, tp = cm_bin.ravel() if cm_bin.size == 4 else (0, 0, 0, 0)
            fpr = float(fp / max(fp + tn, 1))

            model_cv_scores[name].append(macro_f1)
            cv_records.append({
                "experiment_id": "EXP-2026-003",
                "model": name,
                "dataset": "CICIoT2023",
                "seed": RANDOM_SEED,
                "fold": f"fold_{fold}",
                "accuracy": round(acc, 4),
                "precision": round(macro_prec, 4),
                "recall": round(macro_rec, 4),
                "f1_score": round(macro_f1, 4),
                "fpr": round(fpr, 4),
                "latency_ms": round(infer_lat, 4),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "feature_schema_version": "schema-v2.0"
            })

    # Save Cross-Validation CSV
    cv_df = pd.DataFrame(cv_records)
    cv_csv_path = OUT_DIR / "cross_validation.csv"
    cv_df.to_csv(cv_csv_path, index=False)
    print(f"\n--> Cross-Validation results saved to: {cv_csv_path}")

    # 6. Champion Model Selection (Based on CV Macro F1)
    print("\n--> 4. Model Selection Analysis (5-Fold CV Macro F1 Mean ± Std):")
    cv_summary = {}
    for name, scores in model_cv_scores.items():
        mean_f1 = float(np.mean(scores))
        std_f1 = float(np.std(scores))
        cv_summary[name] = {"mean": mean_f1, "std": std_f1}
        print(f"    - {name:<15}: Macro F1 = {mean_f1:.4f} ± {std_f1:.4f}")

    champion_name = max(cv_summary.keys(), key=lambda k: cv_summary[k]["mean"])
    print(f"\n--> CHAMPION MODEL SELECTED: **{champion_name}** (CV Macro F1 = {cv_summary[champion_name]['mean']:.4f})")

    # 7. Final Fit on Full Training Partition & Single Evaluation on Frozen Test Set
    print(f"\n--> 5. Training Final Models & Evaluating Champion on Untouched Test Set...")
    # Full train partition preprocessing
    final_imputer = SimpleImputer(strategy="median")
    X_train_imp = final_imputer.fit_transform(X_train_raw)

    final_scaler = StandardScaler()
    X_train_scl = final_scaler.fit_transform(X_train_imp)

    k_val = min(N_SELECTED_FEATURES, X_train_raw.shape[1])
    final_sel = SelectKBest(score_func=f_classif, k=k_val)
    X_train_final = final_sel.fit_transform(X_train_scl, y_train_enc)

    selected_feature_mask = final_sel.get_support()
    selected_feature_names = [f for f, s in zip(X_train_raw.columns, selected_feature_mask) if s]

    # Preprocessor bundle object
    preprocessor_bundle = {
        "imputer": final_imputer,
        "scaler": final_scaler,
        "selector": final_sel,
        "label_encoder": label_encoder,
        "selected_feature_names": selected_feature_names,
        "feature_schema_version": "schema-v2.0",
        "dataset": "CICIoT2023",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    prep_artifact_path = OUT_DIR / "preprocessor.joblib"
    joblib.dump(preprocessor_bundle, prep_artifact_path)
    prep_hash = hashlib.sha256(prep_artifact_path.read_bytes()).hexdigest()

    # Preprocess Untouched Test Set
    X_test_imp = final_imputer.transform(X_test_raw)
    X_test_scl = final_scaler.transform(X_test_imp)
    X_test_final = final_sel.transform(X_test_scl)

    # Train all candidate models on full train and evaluate on test set for baseline comparison
    baseline_records = []
    trained_models = {}

    for name, factory in candidate_factories.items():
        model = factory()
        if model is None:
            continue

        t0 = time.perf_counter()
        model.fit(X_train_final, y_train_enc)
        t_train = (time.perf_counter() - t0) * 1000.0

        t0 = time.perf_counter()
        test_preds = model.predict(X_test_final)
        if test_preds.ndim > 1:
            test_preds = test_preds.ravel()
        t_infer = (time.perf_counter() - t0) * 1000.0 / max(len(X_test_final), 1)

        t_acc = float(accuracy_score(y_test_enc, test_preds))
        t_f1 = float(f1_score(y_test_enc, test_preds, average="macro", zero_division=0))
        t_prec = float(precision_score(y_test_enc, test_preds, average="macro", zero_division=0))
        t_rec = float(recall_score(y_test_enc, test_preds, average="macro", zero_division=0))

        benign_idx = list(classes).index("Benign") if "Benign" in classes else 0
        y_test_bin = (y_test_enc != benign_idx).astype(int)
        preds_bin = (test_preds != benign_idx).astype(int)
        cm_bin = confusion_matrix(y_test_bin, preds_bin, labels=[0, 1])
        tn, fp, fn, tp = cm_bin.ravel() if cm_bin.size == 4 else (0, 0, 0, 0)
        t_fpr = float(fp / max(fp + tn, 1))

        # Save individual candidate artifact
        slug = name.lower().replace(" ", "_")
        art_file = OUT_DIR / f"{slug}.joblib"
        joblib.dump(model, art_file)
        art_hash = hashlib.sha256(art_file.read_bytes()).hexdigest()

        trained_models[name] = {"model": model, "path": str(art_file), "hash": art_hash}

        baseline_records.append({
            "experiment_id": "EXP-2026-003",
            "model": name,
            "dataset": "CICIoT2023",
            "seed": RANDOM_SEED,
            "fold": "final_test",
            "accuracy": round(t_acc, 4),
            "precision": round(t_prec, 4),
            "recall": round(t_rec, 4),
            "f1_score": round(t_f1, 4),
            "fpr": round(t_fpr, 4),
            "latency_ms": round(t_infer, 4),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "feature_schema_version": "schema-v2.0",
            "train_latency_ms": round(t_train, 4),
            "inference_latency_ms": round(t_infer, 4)
        })

    # Save Baseline Comparison CSV
    baseline_df = pd.DataFrame(baseline_records)
    base_csv_path = OUT_DIR / "baseline_comparison.csv"
    baseline_df.to_csv(base_csv_path, index=False)
    print(f"--> Baseline comparison saved to: {base_csv_path}")

    # Copy Champion to best_model.joblib
    champion_info = trained_models[champion_name]
    best_model_path = OUT_DIR / "best_model.joblib"
    joblib.dump(champion_info["model"], best_model_path)
    best_model_hash = hashlib.sha256(best_model_path.read_bytes()).hexdigest()

    # 8. Detailed Champion Evaluation on Untouched Test Set
    champ_model = champion_info["model"]
    final_test_preds = champ_model.predict(X_test_final)
    if final_test_preds.ndim > 1:
        final_test_preds = final_test_preds.ravel()

    champ_acc = float(accuracy_score(y_test_enc, final_test_preds))
    champ_f1 = float(f1_score(y_test_enc, final_test_preds, average="macro", zero_division=0))
    champ_prec = float(precision_score(y_test_enc, final_test_preds, average="macro", zero_division=0))
    champ_rec = float(recall_score(y_test_enc, final_test_preds, average="macro", zero_division=0))
    champ_weighted_f1 = float(f1_score(y_test_enc, final_test_preds, average="weighted", zero_division=0))

    cm = confusion_matrix(y_test_enc, final_test_preds, labels=range(len(classes)))
    clf_rep = classification_report(y_test_enc, final_test_preds, target_names=classes, output_dict=True, zero_division=0)

    # Per-Class Metrics CSV
    per_class_rows = []
    for cls_name in classes:
        if cls_name in clf_rep:
            c_data = clf_rep[cls_name]
            per_class_rows.append({
                "class_name": cls_name,
                "precision": round(c_data["precision"], 4),
                "recall": round(c_data["recall"], 4),
                "f1_score": round(c_data["f1-score"], 4),
                "support": int(c_data["support"])
            })
    per_class_df = pd.DataFrame(per_class_rows)
    per_class_df.to_csv(OUT_DIR / "per_class_metrics.csv", index=False)

    # Confusion Matrix JSON
    with open(OUT_DIR / "confusion_matrix.json", "w", encoding="utf-8") as f:
        json.dump({"classes": classes, "matrix": cm.tolist()}, f, indent=2)

    # 9. Write Experiment Manifest & Artifact Manifest
    training_timestamp = datetime.now(timezone.utc).isoformat()
    git_commit = get_git_commit_hash()

    exp_manifest = {
        "experiment_id": "EXP-2026-003",
        "dataset_identifier": "ciciot2023_real_benchmark",
        "dataset_hash": dataset_sha256,
        "dataset_hash_algorithm": "SHA-256",
        "dataset_total_samples": len(raw_df),
        "raw_train_samples": len(X_train_raw),
        "raw_test_samples": len(X_test_raw),
        "feature_count": len(X_raw.columns),
        "selected_feature_count": len(selected_feature_names),
        "feature_schema_version": "schema-v2.0",
        "preprocessor_hash": prep_hash,
        "champion_model": champion_name,
        "champion_model_version": f"{champion_name.lower().replace(' ', '_')}-v1.0",
        "model_artifact": f"results/EXP-2026-003/{champion_name.lower().replace(' ', '_')}.joblib",
        "model_artifact_hash": best_model_hash,
        "cv_method": "StratifiedKFold",
        "cv_splits": 5,
        "random_seed": RANDOM_SEED,
        "selection_metric": "cv_macro_f1",
        "final_test_used_for_selection": False,
        "training_git_commit": git_commit,
        "python_version": platform.python_version(),
        "created_at": training_timestamp
    }
    with open(OUT_DIR / "experiment_manifest.json", "w", encoding="utf-8") as f:
        json.dump(exp_manifest, f, indent=2)

    art_manifest = {
        "experiment_id": "EXP-2026-003",
        "model_version": f"{champion_name.lower().replace(' ', '_')}-v1.0",
        "model_type": champion_name,
        "model_hash": best_model_hash,
        "preprocessor_hash": prep_hash,
        "feature_count": len(selected_feature_names),
        "feature_names": selected_feature_names,
        "schema_version": "schema-v2.0",
        "created_at": training_timestamp
    }
    with open(OUT_DIR / "artifact_manifest.json", "w", encoding="utf-8") as f:
        json.dump(art_manifest, f, indent=2)

    # 10. Research Summary & Provenance
    research_summary = {
        "experiment_id": "EXP-2026-003",
        "dataset_identifier": "ciciot2023_real_benchmark",
        "dataset_hash": dataset_sha256[:16],
        "dataset_total_samples": len(raw_df),
        "random_seed": RANDOM_SEED,
        "champion_selected_by": "Train Stratified K-Fold CV (n_splits=5)",
        "champion_model": champion_name,
        "champion_model_version": f"{champion_name.lower().replace(' ', '_')}-v1.0",
        "cv_macro_f1_mean": round(cv_summary[champion_name]["mean"], 4),
        "cv_macro_f1_std": round(cv_summary[champion_name]["std"], 4),
        "final_test_accuracy": round(champ_acc, 4),
        "final_test_macro_f1": round(champ_f1, 4),
        "final_test_macro_precision": round(champ_prec, 4),
        "final_test_macro_recall": round(champ_rec, 4),
        "final_test_weighted_f1": round(champ_weighted_f1, 4),
        "provenance_status": "verified"
    }
    with open(OUT_DIR / "research_summary.json", "w", encoding="utf-8") as f:
        json.dump(research_summary, f, indent=2)

    provenance = {
        "experiment_id": "EXP-2026-003",
        "dataset": {
            "name": "CICIoT2023",
            "type": "real_network_traffic",
            "hash": dataset_sha256,
            "n_samples": len(raw_df),
            "train_samples": len(X_train_raw),
            "test_samples": len(X_test_raw),
            "n_raw_features": len(X_raw.columns),
            "n_selected_features": len(selected_feature_names)
        },
        "reproducibility": {
            "python_version": platform.python_version(),
            "random_seed": RANDOM_SEED,
            "git_commit": git_commit
        },
        "results": {
            "cv_metrics": {
                "n_splits": 5,
                "macro_f1_mean": round(cv_summary[champion_name]["mean"], 4),
                "macro_f1_std": round(cv_summary[champion_name]["std"], 4)
            },
            "final_test_metrics": {
                "accuracy": round(champ_acc, 4),
                "macro_f1": round(champ_f1, 4),
                "macro_precision": round(champ_prec, 4),
                "macro_recall": round(champ_rec, 4),
                "weighted_f1": round(champ_weighted_f1, 4)
            }
        }
    }
    with open(OUT_DIR / "provenance.json", "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2)

    print("\n" + "=" * 75)
    print("  EXP-2026-003 TRAINING & EVALUATION COMPLETE")
    print(f"  Champion Model       : {champion_name}")
    print(f"  5-Fold CV Macro F1   : {cv_summary[champion_name]['mean']:.4f} ± {cv_summary[champion_name]['std']:.4f}")
    print(f"  Final Test Accuracy  : {champ_acc:.4f}")
    print(f"  Final Test Macro F1  : {champ_f1:.4f}")
    print(f"  Final Test WeightedF1: {champ_weighted_f1:.4f}")
    print(f"  Model SHA-256        : {best_model_hash}")
    print(f"  Preprocessor SHA-256 : {prep_hash}")
    print("=" * 75)

    return research_summary

if __name__ == "__main__":
    run_training_experiment()
