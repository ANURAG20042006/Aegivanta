import os
import json
import hashlib
import pytest
import joblib
import pandas as pd
from pathlib import Path
from ml.dataset.generator import CICIDS2017DataGenerator
from ml.dataset.cicids2017_schema import CICIDS2017_FEATURES, ATTACK_CLASSES
from ml.schema.feature_schema import DEFAULT_FEATURE_SCHEMA


class TestPhaseAEvidenceIntegrity:
    """
    Phase A Evidence & Provenance Integrity Test Suite:
    Fails closed on any empirical contradiction, metadata discrepancy, or provenance violation.
    """

    @pytest.fixture(autouse=True)
    def setup_paths(self):
        self.root = Path(__file__).resolve().parents[2]
        self.artifacts_dir = self.root / "ml" / "artifacts"
        self.results_dir = self.root / "results" / "EXP-2026-002"
        self.exp_manifest_path = self.results_dir / "experiment_manifest.json"
        self.art_manifest_path = self.results_dir / "artifact_manifest.json"
        self.meta_path = self.artifacts_dir / "metadata.json"
        self.prov_path = self.artifacts_dir / "provenance.json"
        self.inventory_path = self.root / "PHASE_A_EVIDENCE_INVENTORY.md"
        self.version_matrix_path = self.root / "docs" / "VERSION_MATRIX.md"

    def test_01_experiment_id_consistency(self):
        """1. Verify Experiment ID is consistent across all manifest, provenance, and metadata files."""
        assert self.exp_manifest_path.exists(), "experiment_manifest.json missing!"
        exp_m = json.load(self.exp_manifest_path.open("r", encoding="utf-8"))
        art_m = json.load(self.art_manifest_path.open("r", encoding="utf-8"))
        meta = json.load(self.meta_path.open("r", encoding="utf-8"))
        prov = json.load(self.prov_path.open("r", encoding="utf-8"))

        expected_id = "EXP-2026-002"
        assert exp_m.get("experiment_id") == expected_id
        assert art_m.get("experiment_id") == expected_id
        assert meta.get("experiment_id") == expected_id
        assert prov.get("experiment_id") == expected_id

    def test_02_dataset_hash_consistency(self):
        """2. Verify dataset hash matches the deterministic generation hash."""
        meta = json.load(self.meta_path.open("r", encoding="utf-8"))
        prov = json.load(self.prov_path.open("r", encoding="utf-8"))
        exp_m = json.load(self.exp_manifest_path.open("r", encoding="utf-8"))

        expected_prefix = "63a0675954f5e1d9"
        assert meta.get("dataset_hash") == expected_prefix
        assert prov["dataset"]["hash"] == expected_prefix
        assert exp_m.get("dataset_hash").startswith(expected_prefix)

        # Re-generate dataset and verify deterministic SHA-256 computation
        df = CICIDS2017DataGenerator.generate_synthetic_dataset(num_samples=5000, random_seed=42)
        computed_full_hash = hashlib.sha256(df.to_csv().encode("utf-8")).hexdigest()
        assert computed_full_hash.startswith(expected_prefix)
        assert exp_m.get("dataset_hash") == computed_full_hash

    def test_03_dataset_sample_counts_consistency(self):
        """3. Verify dataset raw, train, test, and SMOTE sample counts are strictly consistent."""
        exp_m = json.load(self.exp_manifest_path.open("r", encoding="utf-8"))
        prov = json.load(self.prov_path.open("r", encoding="utf-8"))
        meta = json.load(self.meta_path.open("r", encoding="utf-8"))

        assert exp_m["dataset_total_samples"] == 5000
        assert exp_m["raw_train_samples"] == 4000
        assert exp_m["raw_test_samples"] == 1000
        assert exp_m["smote_train_samples"] == 25506

        assert prov["dataset"]["n_samples"] == 5000
        assert prov["dataset"]["train_samples"] == 25506
        assert prov["dataset"]["test_samples"] == 1000

        assert meta["training_metrics"]["train_sample_count"] == 25506

        # Verify baseline matrix artifact actually matches this shape
        baseline_p = self.artifacts_dir / "baseline_X_train.joblib"
        assert baseline_p.exists()
        mat = joblib.load(baseline_p)
        assert mat.shape == (25506, 30)

    def test_04_cv_split_consistency(self):
        """4. Verify Cross-Validation configuration across metadata and provenance."""
        meta = json.load(self.meta_path.open("r", encoding="utf-8"))
        prov = json.load(self.prov_path.open("r", encoding="utf-8"))
        exp_m = json.load(self.exp_manifest_path.open("r", encoding="utf-8"))

        assert exp_m["cv_method"] == "StratifiedKFold"
        assert exp_m["cv_splits"] == 5
        assert exp_m["random_seed"] == 42

        assert prov["cross_validation"]["method"] == "StratifiedKFold"
        assert prov["cross_validation"]["n_splits"] == 5
        assert prov["cross_validation"]["random_state"] == 42

        assert meta["cv_metrics"]["n_splits"] == 5
        assert len(meta["cv_metrics"]["fold_details"]) == 5

    def test_05_champion_model_consistency(self):
        """5. Verify champion model identity is unambiguously CatBoost across all files."""
        meta = json.load(self.meta_path.open("r", encoding="utf-8"))
        prov = json.load(self.prov_path.open("r", encoding="utf-8"))
        exp_m = json.load(self.exp_manifest_path.open("r", encoding="utf-8"))
        art_m = json.load(self.art_manifest_path.open("r", encoding="utf-8"))

        assert exp_m["champion_model"] == "CatBoost"
        assert exp_m["champion_model_version"] == "catboost-v1.0"

        assert prov["model"]["name"] == "CatBoost"
        assert prov["model"]["model_version"] == "catboost-v1.0"

        assert meta["model_version"] == "catboost-v1.0"
        assert art_m["champion_model"] == "CatBoost"
        assert art_m["model_version"] == "catboost-v1.0"

    def test_06_model_artifact_hash(self):
        """6. Verify SHA-256 hash of best_model.joblib matches manifest and catboost.joblib."""
        best_p = self.artifacts_dir / "best_model.joblib"
        catboost_p = self.artifacts_dir / "catboost.joblib"
        assert best_p.exists()
        assert catboost_p.exists()

        best_hash = hashlib.sha256(best_p.read_bytes()).hexdigest()
        catboost_hash = hashlib.sha256(catboost_p.read_bytes()).hexdigest()

        # best_model.joblib must be identical to catboost.joblib
        assert best_hash == catboost_hash

        exp_m = json.load(self.exp_manifest_path.open("r", encoding="utf-8"))
        art_m = json.load(self.art_manifest_path.open("r", encoding="utf-8"))
        prov = json.load(self.prov_path.open("r", encoding="utf-8"))

        assert exp_m["model_artifact_hash"] == best_hash
        assert art_m["model_hash"] == best_hash
        assert prov["model"]["artifact_sha256"] == best_hash

    def test_07_preprocessor_hash(self):
        """7. Verify SHA-256 hash of preprocessor.joblib matches manifests."""
        prep_p = self.artifacts_dir / "preprocessor.joblib"
        assert prep_p.exists()

        prep_hash = hashlib.sha256(prep_p.read_bytes()).hexdigest()
        exp_m = json.load(self.exp_manifest_path.open("r", encoding="utf-8"))
        art_m = json.load(self.art_manifest_path.open("r", encoding="utf-8"))

        assert exp_m["preprocessor_hash"] == prep_hash
        assert art_m["preprocessor_hash"] == prep_hash

    def test_08_model_version_consistency(self):
        """8. Verify model versions match naming schema across all artifacts."""
        art_m = json.load(self.art_manifest_path.open("r", encoding="utf-8"))
        for model_name, spec in art_m.get("artifacts", {}).items():
            expected_ver = f"{model_name.lower().replace(' ', '_')}-v1.0"
            assert spec["model_version"] == expected_ver

    def test_09_feature_count_and_schema_consistency(self):
        """9. Verify feature schema dimensions: 78 raw features, 30 selected features."""
        exp_m = json.load(self.exp_manifest_path.open("r", encoding="utf-8"))
        art_m = json.load(self.art_manifest_path.open("r", encoding="utf-8"))
        meta = json.load(self.meta_path.open("r", encoding="utf-8"))

        assert exp_m["feature_count"] == 78
        assert art_m["raw_feature_count"] == 78
        assert art_m["processed_feature_count"] == 30
        assert len(art_m["selected_features"]) == 30
        assert len(meta["selected_features"]) == 30
        assert art_m["model_n_features_in"] == 30

    def test_10_xai_model_provenance(self):
        """10. Verify RealModelExplainer produces model_version matching prediction."""
        from ml.explainability.real_explainer import RealModelExplainer
        import numpy as np

        model = joblib.load(self.artifacts_dir / "best_model.joblib")
        feature_names = [f"f_{i}" for i in range(30)]
        explainer = RealModelExplainer(model, feature_names)

        sample = np.zeros((1, 30))
        result = explainer.explain_instance(
            processed_vector=sample,
            model_version="catboost-v1.0",
            prediction="BENIGN",
            confidence=0.98
        )

        assert result["model_version"] == "catboost-v1.0"
        assert result["prediction"] == "BENIGN"
        assert result["confidence"] == 0.98

    def test_11_synthetic_benchmark_labeling(self):
        """11. Verify README and docs clearly disclose synthetic benchmark status."""
        readme = (self.root / "README.md").read_text(encoding="utf-8", errors="ignore")
        docs = (self.root / "docs" / "DOCUMENTATION.md").read_text(encoding="utf-8", errors="ignore")

        assert "synthetic_cicids2017_benchmark" in readme
        assert "Synthetic Benchmark Disclosure" in readme or "synthetic" in readme.lower()
        assert "EVIDENCE & PROVENANCE INTEGRITY NOTICE" in docs

    def test_12_production_vs_benchmark_metric_labeling(self):
        """12. Verify latency metrics differentiate between micro-benchmark and live pipeline."""
        readme = (self.root / "README.md").read_text(encoding="utf-8", errors="ignore")
        assert "Inference Latency (Micro-Benchmark)" in readme or "Micro-Benchmark" in readme
        assert "End-to-End Live Pipeline Latency" in readme or "Live Pipeline" in readme

    def test_13_unsupported_certification_claims_are_corrected(self):
        """13. Verify that unsupported external certification claims are corrected."""
        readme = (self.root / "README.md").read_text(encoding="utf-8", errors="ignore")
        docs = (self.root / "docs" / "DOCUMENTATION.md").read_text(encoding="utf-8", errors="ignore")

        assert "Not externally certified" in readme or "Self-attested technical implementation" in readme
        assert "Not externally certified" in docs or "not currently externally certified" in docs.lower()

    def test_14_experiment_manifest_integrity(self):
        """14. Verify experiment_manifest.json contains all required non-null fields."""
        assert self.exp_manifest_path.exists()
        exp_m = json.load(self.exp_manifest_path.open("r", encoding="utf-8"))

        required_keys = [
            "experiment_id", "dataset_identifier", "dataset_hash", "dataset_hash_algorithm",
            "dataset_total_samples", "raw_train_samples", "raw_test_samples", "smote_train_samples",
            "feature_count", "feature_schema_hash", "label_schema_hash", "preprocessor_version",
            "preprocessor_hash", "champion_model", "champion_model_version", "model_artifact",
            "model_artifact_hash", "cv_method", "cv_splits", "random_seed", "selection_metric",
            "selection_dataset", "final_test_used_for_selection", "training_git_commit",
            "python_version", "dependency_lock_hash", "created_at"
        ]

        for k in required_keys:
            assert k in exp_m, f"Key '{k}' missing from experiment_manifest.json"
            assert exp_m[k] is not None, f"Key '{k}' in experiment_manifest.json cannot be None"
