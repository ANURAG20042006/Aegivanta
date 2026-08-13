"""
tests/ml/test_experiment_provenance.py
======================================
Comprehensive test suite verifying Experiment Provenance, Metadata Consistency,
Artifact Hashes, Configuration Traceability, and Historical Benchmark Separation.
"""

import json
import hashlib
from pathlib import Path
import pytest
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class TestExperimentProvenance:

    @pytest.fixture
    def metadata(self):
        meta_path = PROJECT_ROOT / "ml/artifacts/metadata.json"
        assert meta_path.exists(), "ml/artifacts/metadata.json missing"
        with meta_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture
    def manifest(self):
        manifest_path = PROJECT_ROOT / "ml/artifacts/artifact_manifest.json"
        assert manifest_path.exists(), "ml/artifacts/artifact_manifest.json missing"
        with manifest_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture
    def provenance(self):
        prov_path = PROJECT_ROOT / "results/EXP-2026-002/provenance.json"
        assert prov_path.exists(), "results/EXP-2026-002/provenance.json missing"
        with prov_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def test_1_experiment_id_consistency(self, metadata, manifest, provenance):
        """Experiment ID must be consistent across all artifacts."""
        assert metadata.get("experiment_id") == "EXP-2026-002"
        assert manifest.get("experiment_id") == "EXP-2026-002"
        assert provenance.get("experiment_id") == "EXP-2026-002"

    def test_2_dataset_provenance_and_hash(self, metadata, provenance):
        """Dataset provenance must record synthetic type, seed, and non-empty hash."""
        assert metadata.get("dataset_identifier") == "synthetic_cicids2017_benchmark"
        assert metadata.get("random_seed") == 42
        assert metadata.get("dataset_hash") is not None
        assert provenance["dataset"]["type"] == "synthetic"
        assert provenance["dataset"]["hash"] == metadata["dataset_hash"]

    def test_3_model_artifact_hash_match(self, manifest, provenance):
        """Saved best_model.joblib SHA256 must match manifest and provenance hashes."""
        model_path = PROJECT_ROOT / "ml/artifacts/best_model.joblib"
        assert model_path.exists()
        actual_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
        assert actual_hash == manifest.get("model_hash")
        assert actual_hash == provenance["model"]["artifact_sha256"]

    def test_4_preprocessor_artifact_hash_match(self, manifest):
        """Saved preprocessor.joblib SHA256 must match manifest hash."""
        prep_path = PROJECT_ROOT / "ml/artifacts/preprocessor.joblib"
        assert prep_path.exists()
        actual_hash = hashlib.sha256(prep_path.read_bytes()).hexdigest()
        assert actual_hash == manifest.get("preprocessor_hash")

    def test_5_dimension_provenance_and_compatibility(self, manifest):
        """Model input dimension must match preprocessor selected features (30 == 30)."""
        model_path = PROJECT_ROOT / "ml/artifacts/best_model.joblib"
        prep_path = PROJECT_ROOT / "ml/artifacts/preprocessor.joblib"

        loaded_model = joblib.load(model_path)
        loaded_prep = joblib.load(prep_path)

        inner = getattr(loaded_model, "model", loaded_model)
        model_dim = getattr(inner, "n_features_in_", None)
        if (not model_dim or model_dim == 0) and hasattr(inner, "feature_names_") and inner.feature_names_:
            model_dim = len(inner.feature_names_)

        prep_dim = len(getattr(loaded_prep, "selected_feature_names", []))

        assert prep_dim == 30
        assert model_dim == 30
        assert manifest.get("model_n_features_in") == 30

    def test_6_cv_and_split_provenance(self, metadata, provenance):
        """CV and split configurations must match across metadata and provenance."""
        assert metadata.get("cv_metrics", {}).get("n_splits") == 3
        assert provenance["cross_validation"]["n_splits"] == 3
        assert provenance["cross_validation"]["method"] == "StratifiedKFold"
        assert provenance["split"]["test_size"] == 0.2
        assert provenance["split"]["stratified"] is True

    def test_7_historical_benchmark_isolation(self):
        """Historical benchmarks must be isolated in research/reference and not marked active."""
        hist_path = PROJECT_ROOT / "research/reference/historical_benchmarks.json"
        assert hist_path.exists()
        with hist_path.open("r", encoding="utf-8") as f:
            hist_data = json.load(f)
        assert "baselines" in hist_data
        assert len(hist_data["baselines"]) >= 3
        assert "EXP-2026-001" in hist_data.get("_description", "")

    def test_8_package_versions_provenance(self, metadata):
        """Package versions recorded in metadata must match tested core environment."""
        lib_ver = metadata.get("library_versions", {})
        assert lib_ver.get("scikit-learn") == "1.6.1"
        assert lib_ver.get("numpy") == "2.2.2"
        assert lib_ver.get("pandas") == "2.2.3"
