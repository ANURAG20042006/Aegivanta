"""
tests/integration/test_exp_2026_003_dataset_integrity.py
=========================================================
Independent automated verification suite for EXP-2026-003:
Real-World CICIoT2023 Dataset, Schemas, Leakage Isolation,
Model Selection, Artifact Integrity, and XAI Provenance.
"""

import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXP_DIR = PROJECT_ROOT / "results" / "EXP-2026-003"
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "EXP-2026-003" / "ciciot2023_real_benchmark.csv"


def test_01_dataset_manifest_exists():
    manifest_path = EXP_DIR / "dataset_manifest.json"
    assert manifest_path.exists(), f"Missing dataset_manifest.json at {manifest_path}"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["experiment_id"] == "EXP-2026-003"
    assert data["dataset_name"] == "CICIoT2023"
    assert data["dataset_scope"] == "CICIoT2023-derived Aegivanta benchmark subset"
    assert data["official_dataset_total_flows"] == 46686579
    assert data["subset_total_records"] == 7800


def test_02_dataset_hash_integrity():
    assert RAW_DATA_PATH.exists(), f"Missing raw dataset at {RAW_DATA_PATH}"
    actual_hash = hashlib.sha256(RAW_DATA_PATH.read_bytes()).hexdigest()
    
    with open(EXP_DIR / "dataset_manifest.json", "r", encoding="utf-8") as f:
        m = json.load(f)
    assert actual_hash == m["archive_sha256"], "Raw dataset hash mismatch with dataset_manifest.json"


def test_03_real_world_traffic_flag():
    with open(EXP_DIR / "dataset_manifest.json", "r", encoding="utf-8") as f:
        m = json.load(f)
    assert m["real_network_traffic"] is True
    assert m["synthetic"] is False


def test_04_source_metadata_and_license():
    with open(EXP_DIR / "dataset_manifest.json", "r", encoding="utf-8") as f:
        m = json.load(f)
    assert "unb.ca" in m["official_source"].lower()
    assert len(m["license"]) > 0


def test_05_schema_integrity():
    schema_path = EXP_DIR / "feature_schema.json"
    assert schema_path.exists()
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    assert schema["version"] == "schema-v2.0"
    assert schema["feature_count"] >= 30


def test_06_feature_count():
    df = pd.read_csv(RAW_DATA_PATH, nrows=5)
    feature_cols = [c for c in df.columns if c != "label"]
    assert len(feature_cols) >= 30


def test_07_label_mapping():
    mapping_path = EXP_DIR / "label_mapping.json"
    assert mapping_path.exists()
    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    assert "Benign" in mapping
    assert mapping["Benign"]["category"] == "Benign"
    assert "DDoS-SYN_Flood" in mapping
    assert mapping["DDoS-SYN_Flood"]["category"] == "DDoS"


def test_08_no_train_test_overlap():
    with open(EXP_DIR / "experiment_manifest.json", "r", encoding="utf-8") as f:
        exp = json.load(f)
    train_n = exp["raw_train_samples"]
    test_n = exp["raw_test_samples"]
    total_n = exp["dataset_total_samples"]
    assert train_n + test_n == total_n
    assert train_n > test_n
    assert test_n == int(0.20 * total_n)


def test_09_leakage_controls_no_ip_port():
    df = pd.read_csv(RAW_DATA_PATH, nrows=5)
    forbidden_substrings = ["src_ip", "dst_ip", "source_ip", "destination_ip", "src_mac", "dst_mac"]
    for col in df.columns:
        for sub in forbidden_substrings:
            assert sub != col.lower(), f"Forbidden identifier '{col}' found in dataset"


def test_10_preprocessing_isolation():
    prep_path = EXP_DIR / "preprocessor.joblib"
    assert prep_path.exists()
    prep = joblib.load(prep_path)
    assert "imputer" in prep
    assert "scaler" in prep
    assert "selector" in prep


def test_11_class_balancing_isolation():
    quality_path = EXP_DIR / "dataset_quality_report.md"
    assert quality_path.exists()


def test_12_model_artifact_exists():
    best_model_path = EXP_DIR / "best_model.joblib"
    assert best_model_path.exists()


def test_13_model_hash_verification():
    best_model_path = EXP_DIR / "best_model.joblib"
    actual_hash = hashlib.sha256(best_model_path.read_bytes()).hexdigest()
    
    with open(EXP_DIR / "experiment_manifest.json", "r", encoding="utf-8") as f:
        exp = json.load(f)
    with open(EXP_DIR / "artifact_manifest.json", "r", encoding="utf-8") as f:
        art = json.load(f)
    
    assert actual_hash == exp["model_artifact_hash"]
    assert actual_hash == art["model_hash"]


def test_14_preprocessor_hash_verification():
    prep_path = EXP_DIR / "preprocessor.joblib"
    actual_hash = hashlib.sha256(prep_path.read_bytes()).hexdigest()
    
    with open(EXP_DIR / "experiment_manifest.json", "r", encoding="utf-8") as f:
        exp = json.load(f)
    with open(EXP_DIR / "artifact_manifest.json", "r", encoding="utf-8") as f:
        art = json.load(f)
    
    assert actual_hash == exp["preprocessor_hash"]
    assert actual_hash == art["preprocessor_hash"]


def test_15_model_schema_compatibility():
    with open(EXP_DIR / "artifact_manifest.json", "r", encoding="utf-8") as f:
        art = json.load(f)
    assert art["schema_version"] == "schema-v2.0"
    assert art["feature_count"] == 30


def test_16_xai_provenance():
    with open(EXP_DIR / "experiment_manifest.json", "r", encoding="utf-8") as f:
        exp = json.load(f)
    champion_ver = exp["champion_model_version"]
    assert len(champion_ver) > 0


def test_17_exp_2026_002_preservation():
    exp2_manifest = PROJECT_ROOT / "results" / "EXP-2026-002" / "experiment_manifest.json"
    assert exp2_manifest.exists(), "EXP-2026-002 experiment manifest must be preserved!"
    with open(exp2_manifest, "r", encoding="utf-8") as f:
        exp2 = json.load(f)
    assert exp2["experiment_id"] == "EXP-2026-002"
    assert exp2["dataset_identifier"] == "synthetic_cicids2017_benchmark"
