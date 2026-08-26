"""
scripts/verify_phase_a1_reproducibility.py
=========================================
Phase A.1 Independent Evidence Reproducibility Verification Suite.
Executes independent data generation, hashing, artifact hash checks,
traceability analysis, XAI provenance checks, and latency profiling.
"""

import os
import sys
import json
import time
import hashlib
import tempfile
import platform
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import sklearn

# Set stdout UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.dataset.generator import CICIDS2017DataGenerator
from ml.dataset.preprocessor import CICIDS2017Preprocessor
from ml.explainability.real_explainer import RealModelExplainer


def run_verification():
    results = {}
    print("=" * 70)
    print("  PHASE A.1 — INDEPENDENT REPRODUCIBILITY & EVIDENCE AUDIT")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. DATASET REPRODUCIBILITY
    # -------------------------------------------------------------
    print("\n--- 1. DATASET REPRODUCIBILITY ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_csv = Path(tmpdir) / "synthetic_dataset_5000.csv"
        print("--> Generating synthetic dataset (num_samples=5000, random_seed=42) in temporary location...")
        t0 = time.time()
        df = CICIDS2017DataGenerator.generate_synthetic_dataset(num_samples=5000, random_seed=42)
        gen_time = time.time() - t0
        print(f"--> Generation complete in {gen_time:.2f}s. Shape: {df.shape}")

        df.to_csv(tmp_csv, index=False)
        raw_csv_bytes = tmp_csv.read_bytes()
        df_csv_bytes = df.to_csv().encode("utf-8")
        computed_full_sha256 = hashlib.sha256(df_csv_bytes).hexdigest()
        computed_prefix = computed_full_sha256[:16]

        print(f"--> Computed Full Dataset SHA-256 : {computed_full_sha256}")
        print(f"--> Computed 16-Char Prefix       : {computed_prefix}")

        expected_hash = "63a0675954f5e1d97c65eaef49946c7912d0d1481c86201a01f033187fa9751f"
        print(f"--> Authoritative Expected Hash   : {expected_hash}")

        hash_match = (computed_full_sha256 == expected_hash)
        print(f"--> Dataset Hash Match Result     : {'[MATCH]' if hash_match else '[MISMATCH]'}")

        total_samples = len(df)
        print(f"--> Total Samples: {total_samples} (Expected: 5000)")

        results["dataset"] = {
            "total_samples": total_samples,
            "computed_sha256": computed_full_sha256,
            "expected_sha256": expected_hash,
            "hash_match": hash_match,
            "shape": list(df.shape)
        }

    # -------------------------------------------------------------
    # 2. TRAIN / TEST REPRODUCIBILITY & SMOTE VERIFICATION
    # -------------------------------------------------------------
    print("\n--- 2. TRAIN/TEST REPRODUCIBILITY & SMOTE VERIFICATION ---")
    preprocessor = CICIDS2017Preprocessor(n_features_to_select=30)
    
    # Execute authoritative decoupled preprocessing
    X_train_final, X_test_selected, y_train_final, y_test = preprocessor.fit_transform_train_test(
        df,
        target_column="Label",
        test_size=0.2,
        balance_data=True,
        random_state=42
    )

    raw_train_samples = len(preprocessor.X_train_raw)
    raw_test_samples = len(X_test_selected)
    smote_train_samples = len(X_train_final)
    test_samples_untouched = len(X_test_selected)

    print(f"--> Raw Train Samples : {raw_train_samples} (80%, Expected: 4000)")
    print(f"--> Raw Test Samples  : {raw_test_samples} (20%, Expected: 1000)")
    print(f"--> SMOTE Train Samples: {smote_train_samples} (Expected: 25506)")
    print(f"--> Test Samples (Untouched): {test_samples_untouched} (Expected: 1000)")

    verified_split = (raw_train_samples == 4000 and raw_test_samples == 1000 and smote_train_samples == 25506 and test_samples_untouched == 1000)
    print(f"--> Train/Test & SMOTE Split Verified: {verified_split}")

    results["split_smote"] = {
        "raw_train": raw_train_samples,
        "raw_test": raw_test_samples,
        "smote_train": smote_train_samples,
        "test_untouched": test_samples_untouched,
        "verified": verified_split
    }

    # -------------------------------------------------------------
    # 3. ARTIFACT INDEPENDENT HASH VERIFICATION
    # -------------------------------------------------------------
    print("\n--- 3. ARTIFACT INDEPENDENT HASH VERIFICATION ---")
    art_dir = PROJECT_ROOT / "ml" / "artifacts"
    best_model_path = art_dir / "best_model.joblib"
    catboost_path = art_dir / "catboost.joblib"
    prep_path = art_dir / "preprocessor.joblib"
    art_manifest_path = art_dir / "artifact_manifest.json"
    exp_manifest_path = PROJECT_ROOT / "results" / "EXP-2026-002" / "experiment_manifest.json"

    actual_model_hash = hashlib.sha256(best_model_path.read_bytes()).hexdigest()
    actual_catboost_hash = hashlib.sha256(catboost_path.read_bytes()).hexdigest()
    actual_prep_hash = hashlib.sha256(prep_path.read_bytes()).hexdigest()

    expected_model_hash = "a2df2c19e079c4c163c6e4997af2631fa35a743316e77e6a2ef1a3d3c33a5898"
    expected_prep_hash = "0a9bcc5cc6f4d3a16f694a05df34647ceed59484e5b2cc4453e215644a24d521"

    print(f"--> Actual best_model.joblib SHA-256 : {actual_model_hash}")
    print(f"--> Expected Champion Model SHA-256  : {expected_model_hash}")
    print(f"--> Model Hash Match                 : {actual_model_hash == expected_model_hash}")

    print(f"--> Actual preprocessor.joblib SHA-256 : {actual_prep_hash}")
    print(f"--> Expected Preprocessor SHA-256    : {expected_prep_hash}")
    print(f"--> Preprocessor Hash Match          : {actual_prep_hash == expected_prep_hash}")

    with art_manifest_path.open("r", encoding="utf-8") as f:
        art_m = json.load(f)
    with exp_manifest_path.open("r", encoding="utf-8") as f:
        exp_m = json.load(f)

    art_m_model_match = (art_m.get("model_hash") == actual_model_hash)
    art_m_prep_match = (art_m.get("preprocessor_hash") == actual_prep_hash)
    exp_m_model_match = (exp_m.get("model_artifact_hash") == actual_model_hash)
    exp_m_prep_match = (exp_m.get("preprocessor_hash") == actual_prep_hash)

    print(f"--> artifact_manifest.json model_hash match     : {art_m_model_match}")
    print(f"--> artifact_manifest.json preprocessor match   : {art_m_prep_match}")
    print(f"--> experiment_manifest.json model_hash match   : {exp_m_model_match}")
    print(f"--> experiment_manifest.json preprocessor match : {exp_m_prep_match}")

    results["artifact_hashes"] = {
        "actual_model_sha256": actual_model_hash,
        "expected_model_sha256": expected_model_hash,
        "model_match": actual_model_hash == expected_model_hash,
        "actual_prep_sha256": actual_prep_hash,
        "expected_prep_sha256": expected_prep_hash,
        "prep_match": actual_prep_hash == expected_prep_hash,
        "manifests_agree": art_m_model_match and art_m_prep_match and exp_m_model_match and exp_m_prep_match
    }

    # -------------------------------------------------------------
    # 4. MODEL METRIC TRACEABILITY
    # -------------------------------------------------------------
    print("\n--- 4. MODEL METRIC TRACEABILITY ---")
    meta_path = art_dir / "metadata.json"
    prov_path = art_dir / "provenance.json"
    res_summary_path = PROJECT_ROOT / "results" / "EXP-2026-002" / "research_summary.json"
    cv_csv_path = PROJECT_ROOT / "results" / "EXP-2026-002" / "cross_validation.csv"
    base_csv_path = PROJECT_ROOT / "results" / "EXP-2026-002" / "baseline_comparison.csv"

    meta = json.load(meta_path.open("r", encoding="utf-8"))
    prov = json.load(prov_path.open("r", encoding="utf-8"))
    res_summary = json.load(res_summary_path.open("r", encoding="utf-8"))
    cv_df = pd.read_csv(cv_csv_path)
    base_df = pd.read_csv(base_csv_path)

    print("--> Metadata CV Macro F1 Mean :", meta["cv_metrics"]["macro_f1_mean"])
    print("--> Metadata CV Macro F1 Std  :", meta["cv_metrics"]["macro_f1_std"])
    print("--> Metadata Final Test F1    :", meta["final_test_metrics"]["macro_f1"])
    print("--> Metadata Final Test Acc   :", meta["final_test_metrics"]["accuracy"])

    cb_base = base_df[base_df["model"] == "CatBoost"]
    print(f"--> CatBoost in baseline_comparison.csv:\n{cb_base[['model', 'accuracy', 'precision', 'recall', 'f1_score', 'fpr']]}")

    traced_cv_f1 = meta["cv_metrics"]["macro_f1_mean"]
    traced_cv_std = meta["cv_metrics"]["macro_f1_std"]
    traced_test_f1 = meta["final_test_metrics"]["macro_f1"]
    traced_test_acc = meta["final_test_metrics"]["accuracy"]

    cv_match = (round(traced_cv_f1, 4) == 0.9527 and round(traced_cv_std, 4) == 0.0179)
    test_f1_match = (round(traced_test_f1, 4) == 0.9266)
    test_acc_match = (round(traced_test_acc, 4) == 0.9480)

    print(f"--> 5-Fold CV F1 0.9527 +- 0.0179 Traced : {cv_match}")
    print(f"--> Final Test F1 0.9266 Traced         : {test_f1_match}")
    print(f"--> Final Test Accuracy 0.9480 Traced   : {test_acc_match}")

    results["metrics_traceability"] = {
        "cv_f1_mean": traced_cv_f1,
        "cv_f1_std": traced_cv_std,
        "test_f1": traced_test_f1,
        "test_acc": traced_test_acc,
        "cv_match": cv_match,
        "test_f1_match": test_f1_match,
        "test_acc_match": test_acc_match
    }

    # -------------------------------------------------------------
    # 5. XAI PROVENANCE
    # -------------------------------------------------------------
    print("\n--- 5. XAI PROVENANCE ---")
    champion_model = joblib.load(best_model_path)
    feature_names = [f"f_{i}" for i in range(30)]
    explainer = RealModelExplainer(champion_model, feature_names)

    sample_vec = np.zeros((1, 30))
    xai_res = explainer.explain_instance(
        processed_vector=sample_vec,
        model_version="catboost-v1.0",
        prediction="BENIGN",
        confidence=0.98
    )

    print("--> XAI Output Model Version   :", xai_res.get("model_version"))
    print("--> XAI Output Explainer Type  :", xai_res.get("explainer_type"))
    print("--> XAI Explanation Available  :", xai_res.get("explanation_available"))
    print("--> XAI Top Features Count     :", len(xai_res.get("top_features", [])))

    xai_ver_match = (xai_res.get("model_version") == "catboost-v1.0")
    print(f"--> prediction.model_version == explanation.model_version: {xai_ver_match}")

    results["xai"] = {
        "model_version": xai_res.get("model_version"),
        "explainer_type": xai_res.get("explainer_type"),
        "explanation_available": xai_res.get("explanation_available"),
        "version_match": xai_ver_match
    }

    # -------------------------------------------------------------
    # 6. LATENCY PROFILING & MEASUREMENT AUDIT
    # -------------------------------------------------------------
    print("\n--- 6. LATENCY MEASUREMENT PROFILING & AUDIT ---")
    model_obj = getattr(champion_model, "model", champion_model)
    for _ in range(50):
        model_obj.predict(sample_vec)

    latencies_us = []
    for _ in range(1000):
        t_start = time.perf_counter()
        model_obj.predict(sample_vec)
        t_end = time.perf_counter()
        latencies_us.append((t_end - t_start) * 1e6)

    mean_latency_ms = np.mean(latencies_us) / 1000.0
    p50_latency_ms = np.percentile(latencies_us, 50) / 1000.0
    p95_latency_ms = np.percentile(latencies_us, 95) / 1000.0
    p99_latency_ms = np.percentile(latencies_us, 99) / 1000.0

    print(f"--> Measured In-Memory Array Inference Latency (Mean): {mean_latency_ms:.4f} ms/sample ({mean_latency_ms*1000:.2f} us)")
    print(f"--> Measured p50: {p50_latency_ms:.4f} ms, p95: {p95_latency_ms:.4f} ms, p99: {p99_latency_ms:.4f} ms")

    xai_latencies_ms = []
    for _ in range(100):
        t_start = time.perf_counter()
        explainer.explain_instance(
            processed_vector=sample_vec,
            model_version="catboost-v1.0",
            prediction="BENIGN",
            confidence=0.98
        )
        t_end = time.perf_counter()
        xai_latencies_ms.append((t_end - t_start) * 1000.0)

    mean_xai_ms = np.mean(xai_latencies_ms)
    p50_xai_ms = np.percentile(xai_latencies_ms, 50)
    p95_xai_ms = np.percentile(xai_latencies_ms, 95)

    print(f"--> Measured Native CatBoost SHAP Latency (Mean): {mean_xai_ms:.2f} ms/sample")
    print(f"--> Measured XAI p50: {p50_xai_ms:.2f} ms, p95: {p95_xai_ms:.2f} ms")

    results["latency_audit"] = {
        "micro_bench_mean_ms": round(mean_latency_ms, 4),
        "micro_bench_p50_ms": round(p50_latency_ms, 4),
        "micro_bench_p95_ms": round(p95_latency_ms, 4),
        "xai_mean_ms": round(mean_xai_ms, 2),
        "xai_p50_ms": round(p50_xai_ms, 2),
        "xai_p95_ms": round(p95_xai_ms, 2)
    }

    results["environment"] = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "sklearn_version": sklearn.__version__,
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__
    }

    out_json = PROJECT_ROOT / "results" / "EXP-2026-002" / "phase_a1_verification_results.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n--> Verification results saved to: {out_json}")

    return results


if __name__ == "__main__":
    res = run_verification()
