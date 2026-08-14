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
        """Saved catboost.joblib and best_model.joblib SHA256 must match manifest and provenance hashes."""
        cb_path = PROJECT_ROOT / "ml/artifacts/catboost.joblib"
        bm_path = PROJECT_ROOT / "ml/artifacts/best_model.joblib"
        assert cb_path.exists() and cb_path.is_file()
        assert bm_path.exists() and bm_path.is_file()

        actual_cb_hash = hashlib.sha256(cb_path.read_bytes()).hexdigest()
        actual_bm_hash = hashlib.sha256(bm_path.read_bytes()).hexdigest()

        assert actual_cb_hash == actual_bm_hash
        assert actual_cb_hash == manifest.get("model_hash")
        assert actual_cb_hash == provenance["model"]["artifact_sha256"]

    def test_4_preprocessor_artifact_hash_match(self, manifest):
        """Saved preprocessor.joblib SHA256 must match manifest hash."""
        prep_path = PROJECT_ROOT / "ml/artifacts/preprocessor.joblib"
        assert prep_path.exists()
        actual_hash = hashlib.sha256(prep_path.read_bytes()).hexdigest()
        assert actual_hash == manifest.get("preprocessor_hash")

    def test_5_dimension_provenance_and_compatibility(self, manifest):
        """Model input dimension must match preprocessor selected features (30 == 30)."""
        model_path = PROJECT_ROOT / "ml/artifacts/catboost.joblib"
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

    def test_exp_2026_002_provenance_consistency(self, metadata, manifest, provenance):
        """Comprehensive Phase 11 & 12 consistency test for EXP-2026-002."""
        from ml.schema.artifact_mapping import resolve_model_artifact_path

        # 1. Experiment ID
        assert metadata.get("experiment_id") == "EXP-2026-002"
        assert provenance.get("experiment_id") == "EXP-2026-002"
        assert manifest.get("experiment_id") == "EXP-2026-002"

        # 2. Provenance champion == metadata champion
        meta_champ = "CatBoost"
        assert provenance["model"]["name"] == meta_champ
        assert metadata.get("model_version") == "catboost-v1.0"
        assert provenance["model"]["model_version"] == "catboost-v1.0"

        # 3. Research summary champion == authoritative champion
        summary_path = PROJECT_ROOT / "results/EXP-2026-002/research_summary.json"
        assert summary_path.exists()
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        assert summary.get("champion_model") == "CatBoost"
        assert summary.get("best_model") == "CatBoost"

        # 4. Canonical artifact path
        target_path, art_type, actual_sha256, exists = resolve_model_artifact_path("CatBoost")
        assert str(target_path).replace("\\", "/") == "ml/artifacts/catboost.joblib"
        assert art_type == "joblib"

        # 5. Artifact exists
        assert exists is True
        full_artifact_path = PROJECT_ROOT / target_path
        assert full_artifact_path.exists() and full_artifact_path.is_file()

        # 6. Artifact SHA256
        calculated_sha = hashlib.sha256(full_artifact_path.read_bytes()).hexdigest()
        assert calculated_sha == actual_sha256
        assert calculated_sha == provenance["model"]["artifact_sha256"]
        assert calculated_sha == manifest.get("model_hash")

        # 7. Git generation commit
        gen_commit = "75fa5ca9953569752f3392ee55833294e5cec679"
        assert metadata.get("git_commit") == gen_commit
        assert provenance["reproducibility"]["git_commit"] == gen_commit
        assert manifest.get("git_commit") == gen_commit

        # 8. Metrics agreement
        assert metadata["cv_metrics"]["macro_f1_mean"] == 0.9301
        assert provenance["results"]["cv_metrics"]["macro_f1_mean"] == 0.9301
        assert summary["best_cv_f1"] == 0.9301

        assert metadata["final_test_metrics"]["macro_f1"] == 0.9329
        assert provenance["results"]["final_test_metrics"]["macro_f1"] == 0.9329
        assert summary["final_test_macro_f1"] == 0.9329
        assert metadata["final_test_metrics"]["accuracy"] == 0.9600
        assert metadata["final_test_metrics"]["fpr"] == 0.0023

        # 9. Historical benchmarks not used as current experiment metrics
        assert metadata["final_test_metrics"]["macro_f1"] != 0.9901
        assert metadata["final_test_metrics"]["macro_f1"] != 0.9623

        # 10. Phase 12 Artifact Load & Model Type Validation
        loaded = joblib.load(full_artifact_path)
        inner = getattr(loaded, "model", loaded)
        assert "CatBoost" in type(inner).__name__ or "CatBoostClassifier" in type(loaded).__name__
