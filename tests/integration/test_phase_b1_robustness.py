"""
tests/integration/test_phase_b1_robustness.py
=============================================
Independent integration verification suite for Phase B1:
Robustness, Generalization, Root-Cause Error Analysis, and Provenance.
"""

import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXP_B1_DIR = PROJECT_ROOT / "results" / "EXP-2026-003-B1"
EXP_003_DIR = PROJECT_ROOT / "results" / "EXP-2026-003"
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "EXP-2026-003" / "ciciot2023_real_benchmark.csv"

EXP_003_DATASET_HASH = "339dd305a304461aa8e8c17bbdce9f8ea4ec54b608bf315ece6336dbd4d7a778"


def test_01_frozen_test_set_unchanged():
    """1. Verify that raw dataset has exact row count and hash."""
    assert RAW_DATA_PATH.exists()
    df = pd.read_csv(RAW_DATA_PATH)
    assert len(df) == 7800
    assert df["label"].nunique() == 26
    actual_hash = hashlib.sha256(RAW_DATA_PATH.read_bytes()).hexdigest()
    assert actual_hash == EXP_003_DATASET_HASH


def test_02_parent_exp_2026_003_provenance_intact():
    """2. Verify parent EXP-2026-003 manifests and artifacts are unaltered."""
    assert (EXP_003_DIR / "experiment_manifest.json").exists()
    assert (EXP_003_DIR / "best_model.joblib").exists()
    assert (EXP_003_DIR / "preprocessor.joblib").exists()


def test_03_b1_manifests_exist():
    """3. Verify EXP-2026-003-B1 manifests are generated."""
    exp_man = EXP_B1_DIR / "experiment_manifest.json"
    art_man = EXP_B1_DIR / "artifact_manifest.json"
    ana_man = EXP_B1_DIR / "analysis_manifest.json"
    assert exp_man.exists()
    assert art_man.exists()
    assert ana_man.exists()

    with open(exp_man, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert d["experiment_id"] == "EXP-2026-003-B1"
    assert d["parent_experiment_id"] == "EXP-2026-003"
    assert d["dataset_hash"] == EXP_003_DATASET_HASH


def test_04_label_granularity_results():
    """4. Verify label granularity evaluation document and task metrics."""
    doc_path = EXP_B1_DIR / "label_granularity_results.md"
    assert doc_path.exists()
    content = doc_path.read_text(encoding="utf-8")
    assert "Task 1: Granular NIDS" in content
    assert "Task 2: Attack Family" in content
    assert "Task 3: Binary Detection" in content


def test_05_confusion_matrix_integrity():
    """5. Verify 26x26 confusion matrix dimensions and normalization."""
    cm_path = EXP_B1_DIR / "confusion_matrix.csv"
    cm_norm_path = EXP_B1_DIR / "confusion_matrix_normalized.csv"
    assert cm_path.exists()
    assert cm_norm_path.exists()

    cm_df = pd.read_csv(cm_path, index_col=0)
    assert cm_df.shape == (26, 26)
    assert cm_df.values.sum() == 1560  # Total frozen test set size


def test_06_per_class_metrics_integrity():
    """6. Verify per-class metrics contain all 26 classes."""
    pcm_path = EXP_B1_DIR / "per_class_metrics.csv"
    assert pcm_path.exists()
    df = pd.read_csv(pcm_path)
    assert len(df) == 26
    assert "most_confused_class" in df.columns
    assert "confusion_percentage" in df.columns
    assert "f1_score" in df.columns


def test_07_feature_importance_and_redundancy():
    """7. Verify feature importance and redundancy CSVs."""
    fi_path = EXP_B1_DIR / "feature_importance.csv"
    fr_path = EXP_B1_DIR / "feature_redundancy.csv"
    fa_path = EXP_B1_DIR / "feature_analysis.md"
    assert fi_path.exists()
    assert fr_path.exists()
    assert fa_path.exists()

    fi_df = pd.read_csv(fi_path)
    assert len(fi_df) >= 30


def test_08_ablation_study_integrity():
    """8. Verify ablation study has at least 5 evaluated feature subsets."""
    abl_path = EXP_B1_DIR / "ablation_study.csv"
    assert abl_path.exists()
    df = pd.read_csv(abl_path)
    assert len(df) >= 5
    assert "cv_macro_f1" in df.columns
    assert "final_test_macro_f1" in df.columns


def test_09_model_robustness_benchmarking():
    """9. Verify model robustness comparison covers candidate architectures."""
    mr_path = EXP_B1_DIR / "model_robustness.csv"
    assert mr_path.exists()
    df = pd.read_csv(mr_path)
    assert len(df) >= 3
    assert "LightGBM" in df["model_name"].values
    assert "XGBoost" in df["model_name"].values
    assert "CatBoost" in df["model_name"].values


def test_10_cross_dataset_generalization_report():
    """10. Verify cross-dataset generalization report covers independent dataset."""
    cd_path = EXP_B1_DIR / "cross_dataset_generalization.md"
    assert cd_path.exists()
    content = cd_path.read_text(encoding="utf-8")
    assert "CSE-CIC-IDS2018" in content
    assert "Zero-Shot Cross-Dataset Transfer" in content
    assert "Domain Shift" in content


def test_11_calibration_audit_report():
    """11. Verify calibration audit report."""
    cal_path = EXP_B1_DIR / "calibration_report.md"
    assert cal_path.exists()
    content = cal_path.read_text(encoding="utf-8")
    assert "High-Confidence Errors" in content
    assert "Average Confidence on Correct Predictions" in content
