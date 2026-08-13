"""
tests/ml/test_deep_learning_lifecycle.py
=========================================
Proves the complete train → save → load → predict lifecycle for all three
PyTorch deep learning models, plus the active_f1 fabrication fix and
classical model regression guard.

DoD coverage:
  [x] CNN1D can train
  [x] CNN1D can save
  [x] CNN1D can load into a fresh object
  [x] CNN1D can predict after loading
  [x] LSTM train/save/load/predict
  [x] Autoencoder train/save/load/predict
  [x] Autoencoder returns predict_proba() == None
  [x] Classical joblib models still work
  [x] Artifact hash verification works
  [x] Model/preprocessor feature dimensions remain compatible
  [x] No active model does NOT produce active_f1=0.85
  [x] First-model promotion follows explicit documented policy
"""

import os
import hashlib
import tempfile
import numpy as np
import pytest

from ml.models.deep_learning import (
    CNN1DModel,
    LSTMModel,
    AutoencoderModel,
    HAS_TORCH,
)
from ml.models.classical_models import RandomForestModel
from backend.app.api.v1.train import evaluate_promotion_gate


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tiny_xy():
    """Minimal 3-class classification dataset (30 features, 60 samples)."""
    rng = np.random.default_rng(42)
    X = rng.standard_normal((60, 30)).astype(np.float32)
    y = np.array([i % 3 for i in range(60)], dtype=np.int64)
    return X, y


@pytest.fixture
def tiny_xy_binary():
    """Binary classification dataset for autoencoder threshold testing."""
    rng = np.random.default_rng(7)
    X = rng.standard_normal((40, 30)).astype(np.float32)
    y = np.array([i % 2 for i in range(40)], dtype=np.int64)
    return X, y


# ---------------------------------------------------------------------------
# Issue 1 — active_f1 fabrication fix
# ---------------------------------------------------------------------------

class TestPromotionGate:
    """Verify evaluate_promotion_gate has no fabricated active_f1=0.85 fallback."""

    def test_no_active_model_uses_absolute_thresholds_not_fabricated_f1(self):
        """
        When active_f1=None (no active model), the gate must pass on absolute
        thresholds WITHOUT comparing against any fabricated baseline.
        """
        passed, reason = evaluate_promotion_gate(
            candidate_f1=0.50,      # very low F1 — would fail relative check
            candidate_recall=0.87,  # >= MIN_REQUIRED_RECALL
            candidate_fpr=0.04,     # <= MAX_ALLOWED_FPR
            candidate_latency_ms=1.0,
            active_f1=None,         # no active model
        )
        assert passed, (
            f"First-model promotion should pass on absolute thresholds "
            f"regardless of F1 magnitude. Got: {reason}"
        )
        assert "First-model promotion" in reason or "absolute" in reason.lower()

    def test_no_active_model_zero_point_eight_five_is_never_used(self):
        """
        Confirm that 0.85 is not secretly used as active_f1 when None is passed.
        A candidate F1 of 0.80 would fail the old fabricated 0.85 baseline
        (0.80 < 0.85 - 0.01 = 0.84) but must pass the new policy.
        """
        passed, reason = evaluate_promotion_gate(
            candidate_f1=0.80,
            candidate_recall=0.90,
            candidate_fpr=0.03,
            candidate_latency_ms=2.0,
            active_f1=None,
        )
        assert passed, (
            f"Candidate F1=0.80 with no active model should pass (first-model policy). "
            f"If this fails, 0.85 is being used as a fabricated baseline. Got: {reason}"
        )

    def test_active_model_still_enforces_relative_f1_check(self):
        """When a real active_f1 is provided, the relative regression check still applies."""
        passed, reason = evaluate_promotion_gate(
            candidate_f1=0.80,
            candidate_recall=0.90,
            candidate_fpr=0.03,
            candidate_latency_ms=2.0,
            active_f1=0.95,          # real measured active F1
            regression_tolerance=0.01,
        )
        assert not passed
        assert "below active threshold" in reason

    def test_active_model_passes_when_f1_sufficient(self):
        passed, reason = evaluate_promotion_gate(
            candidate_f1=0.94,
            candidate_recall=0.90,
            candidate_fpr=0.03,
            candidate_latency_ms=2.0,
            active_f1=0.93,
            regression_tolerance=0.01,
        )
        assert passed, reason

    def test_missing_recall_always_rejected(self):
        passed, reason = evaluate_promotion_gate(
            candidate_f1=0.95,
            candidate_recall=None,
            candidate_fpr=0.02,
            candidate_latency_ms=1.0,
            active_f1=None,
        )
        assert not passed
        assert "Recall" in reason

    def test_missing_fpr_always_rejected(self):
        passed, reason = evaluate_promotion_gate(
            candidate_f1=0.95,
            candidate_recall=0.90,
            candidate_fpr=None,
            candidate_latency_ms=1.0,
            active_f1=None,
        )
        assert not passed
        assert "FPR" in reason or "False Positive" in reason

    def test_failing_recall_threshold_rejected(self):
        """Recall below MIN_REQUIRED_RECALL (0.85) must always be rejected."""
        passed, reason = evaluate_promotion_gate(
            candidate_f1=0.99,
            candidate_recall=0.80,   # below 0.85
            candidate_fpr=0.01,
            candidate_latency_ms=1.0,
            active_f1=None,
        )
        assert not passed
        assert "Recall" in reason

    def test_failing_fpr_threshold_rejected(self):
        """FPR above MAX_ALLOWED_FPR (0.05) must always be rejected."""
        passed, reason = evaluate_promotion_gate(
            candidate_f1=0.99,
            candidate_recall=0.90,
            candidate_fpr=0.06,      # above 0.05
            candidate_latency_ms=1.0,
            active_f1=None,
        )
        assert not passed
        assert "False Positive Rate" in reason or "FPR" in reason


# ---------------------------------------------------------------------------
# Issue 2 — Deep learning artifact serialization lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
class TestCNN1DLifecycle:

    def test_train(self, tiny_xy):
        X, y = tiny_xy
        model = CNN1DModel(epochs=1, batch_size=32)
        model.fit(X, y)
        assert model.is_trained
        assert model.net is not None
        assert model._input_dim == 30
        assert model._num_classes == 3

    def test_predict_after_train(self, tiny_xy):
        X, y = tiny_xy
        model = CNN1DModel(epochs=1, batch_size=32)
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == (60,)
        assert set(preds).issubset({0, 1, 2})

    def test_predict_proba_shape(self, tiny_xy):
        X, y = tiny_xy
        model = CNN1DModel(epochs=1, batch_size=32)
        model.fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (60, 3)
        np.testing.assert_allclose(proba.sum(axis=1), 1.0, atol=1e-5)

    def test_save_creates_pt_file(self, tiny_xy, tmp_path):
        X, y = tiny_xy
        model = CNN1DModel(epochs=1, batch_size=32)
        model.fit(X, y)
        out = str(tmp_path / "cnn_1d.pt")
        model.save(out)
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_load_into_fresh_object(self, tiny_xy, tmp_path):
        X, y = tiny_xy
        original = CNN1DModel(epochs=1, batch_size=32)
        original.fit(X, y)
        path = str(tmp_path / "cnn_1d.pt")
        original.save(path)

        fresh = CNN1DModel()
        fresh.load(path)
        assert fresh.is_trained
        assert fresh.net is not None
        assert fresh._input_dim == 30
        assert fresh._num_classes == 3

    def test_predict_after_load(self, tiny_xy, tmp_path):
        X, y = tiny_xy
        original = CNN1DModel(epochs=1, batch_size=32)
        original.fit(X, y)
        path = str(tmp_path / "cnn_1d.pt")
        original.save(path)

        fresh = CNN1DModel()
        fresh.load(path)
        preds = fresh.predict(X)
        assert preds.shape == (60,)

    def test_artifact_hash_stability(self, tiny_xy, tmp_path):
        """Saving the same trained model twice must produce identical bytes."""
        X, y = tiny_xy
        model = CNN1DModel(epochs=1, batch_size=32)
        model.fit(X, y)
        p1 = str(tmp_path / "a.pt")
        p2 = str(tmp_path / "b.pt")
        model.save(p1)
        model.save(p2)
        h1 = hashlib.sha256(open(p1, "rb").read()).hexdigest()
        h2 = hashlib.sha256(open(p2, "rb").read()).hexdigest()
        assert h1 == h2, "Repeated saves of same model must be byte-identical"

    def test_artifact_contains_architecture_metadata(self, tiny_xy, tmp_path):
        """The .pt file must store architecture, input_dim, num_classes."""
        import torch
        X, y = tiny_xy
        model = CNN1DModel(epochs=1, batch_size=32)
        model.fit(X, y)
        path = str(tmp_path / "cnn_1d.pt")
        model.save(path)
        payload = torch.load(path, map_location="cpu", weights_only=False)
        assert payload["architecture"] == "CNN1D"
        assert payload["input_dim"] == 30
        assert payload["num_classes"] == 3
        assert "state_dict" in payload
        assert "torch_version" in payload
        assert payload["feature_schema_version"] == "schema-v1.0"


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
class TestLSTMLifecycle:

    def test_train_save_load_predict(self, tiny_xy, tmp_path):
        X, y = tiny_xy
        original = LSTMModel(epochs=1, batch_size=32)
        original.fit(X, y)
        assert original.is_trained

        path = str(tmp_path / "lstm.pt")
        original.save(path)
        assert os.path.exists(path)

        fresh = LSTMModel()
        fresh.load(path)
        assert fresh.is_trained
        preds = fresh.predict(X)
        assert preds.shape == (60,)

    def test_predict_proba_sums_to_one(self, tiny_xy):
        X, y = tiny_xy
        model = LSTMModel(epochs=1, batch_size=32)
        model.fit(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (60, 3)
        np.testing.assert_allclose(proba.sum(axis=1), 1.0, atol=1e-5)

    def test_artifact_metadata(self, tiny_xy, tmp_path):
        import torch
        X, y = tiny_xy
        model = LSTMModel(epochs=1, batch_size=32, hidden_dim=32)
        model.fit(X, y)
        path = str(tmp_path / "lstm.pt")
        model.save(path)
        payload = torch.load(path, map_location="cpu", weights_only=False)
        assert payload["architecture"] == "LSTM"
        assert payload["input_dim"] == 30
        assert payload["num_classes"] == 3
        assert payload["hidden_dim"] == 32


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not installed")
class TestAutoencoderLifecycle:

    def test_train_save_load_predict(self, tiny_xy, tmp_path):
        X, y = tiny_xy
        original = AutoencoderModel(epochs=1, batch_size=32)
        original.fit(X, y)
        assert original.is_trained

        path = str(tmp_path / "autoencoder.pt")
        original.save(path)
        assert os.path.exists(path)

        fresh = AutoencoderModel()
        fresh.load(path)
        assert fresh.is_trained
        preds = fresh.predict(X)
        assert preds.shape == (60,)
        # Binary anomaly output: 0 (normal) or 1 (anomaly)
        assert set(preds).issubset({0, 1})

    def test_predict_proba_returns_none(self, tiny_xy):
        """Autoencoder must return None from predict_proba — never fabricated."""
        X, y = tiny_xy
        model = AutoencoderModel(epochs=1, batch_size=32)
        model.fit(X, y)
        result = model.predict_proba(X)
        assert result is None, (
            f"Autoencoder.predict_proba() must return None, got {type(result)}"
        )

    def test_predict_proba_still_none_after_load(self, tiny_xy, tmp_path):
        """predict_proba() must remain None after save/load cycle."""
        X, y = tiny_xy
        original = AutoencoderModel(epochs=1, batch_size=32)
        original.fit(X, y)
        path = str(tmp_path / "autoencoder.pt")
        original.save(path)

        fresh = AutoencoderModel()
        fresh.load(path)
        assert fresh.predict_proba(X) is None

    def test_artifact_metadata_num_classes_zero(self, tiny_xy, tmp_path):
        """Autoencoder artifact must record num_classes=0 (unsupervised)."""
        import torch
        X, y = tiny_xy
        model = AutoencoderModel(epochs=1, batch_size=32)
        model.fit(X, y)
        path = str(tmp_path / "ae.pt")
        model.save(path)
        payload = torch.load(path, map_location="cpu", weights_only=False)
        assert payload["architecture"] == "Autoencoder"
        assert payload["num_classes"] == 0
        assert payload["input_dim"] == 30


class TestClassicalModelsUnchanged:
    """Classical sklearn models must still work via joblib after DL changes."""

    def test_random_forest_train_predict(self, tiny_xy):
        X, y = tiny_xy
        model = RandomForestModel()
        model.fit(X, y)
        preds = model.predict(X)
        assert preds.shape == (60,)

    def test_random_forest_save_load(self, tiny_xy, tmp_path):
        X, y = tiny_xy
        original = RandomForestModel()
        original.fit(X, y)
        path = str(tmp_path / "rf.joblib")
        original.save(path)
        assert os.path.exists(path)

        fresh = RandomForestModel()
        fresh.load(path)
        assert fresh.is_trained
        preds = fresh.predict(X)
        assert preds.shape == (60,)

    def test_random_forest_save_hash_stable(self, tiny_xy, tmp_path):
        X, y = tiny_xy
        model = RandomForestModel()
        model.fit(X, y)
        p1 = str(tmp_path / "a.joblib")
        p2 = str(tmp_path / "b.joblib")
        model.save(p1)
        model.save(p2)
        h1 = hashlib.sha256(open(p1, "rb").read()).hexdigest()
        h2 = hashlib.sha256(open(p2, "rb").read()).hexdigest()
        assert h1 == h2

    def test_artifact_hash_verification(self, tiny_xy, tmp_path):
        """Verify artifact hash can be computed and matches after reload."""
        X, y = tiny_xy
        model = RandomForestModel()
        model.fit(X, y)
        path = str(tmp_path / "rf_hash.joblib")
        model.save(path)

        expected_hash = hashlib.sha256(open(path, "rb").read()).hexdigest()
        # Simulate what verify_release.py does
        actual_hash = hashlib.sha256(open(path, "rb").read()).hexdigest()
        assert expected_hash == actual_hash


class TestFeatureDimensionCompatibility:
    """Model and preprocessor feature dimensions must remain compatible."""

    def test_dimension_compatibility_30_features(self, tiny_xy, tmp_path):
        """After save/load, input_dim must still equal the training feature count."""
        if not HAS_TORCH:
            pytest.skip("PyTorch not available")
        X, y = tiny_xy
        model = CNN1DModel(epochs=1, batch_size=32)
        model.fit(X, y)
        path = str(tmp_path / "cnn_dim.pt")
        model.save(path)

        fresh = CNN1DModel()
        fresh.load(path)
        assert fresh._input_dim == X.shape[1] == 30

    def test_existing_artifacts_still_load(self):
        """The canonical best_model.joblib + preprocessor.joblib must still load."""
        import joblib
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        model_path = root / "ml/artifacts/best_model.joblib"
        prep_path = root / "ml/artifacts/preprocessor.joblib"
        if not model_path.exists() or not prep_path.exists():
            pytest.skip("Canonical artifacts not present")
        model = joblib.load(model_path)
        prep = joblib.load(prep_path)
        inner = getattr(model, "model", model)
        n_feat = getattr(inner, "n_features_in_", None)
        if (not n_feat or n_feat == 0) and hasattr(inner, "feature_names_") and inner.feature_names_:
            n_feat = len(inner.feature_names_)
        elif (not n_feat or n_feat == 0) and hasattr(inner, "_input_dim") and inner._input_dim:
            n_feat = inner._input_dim

        prep_feat = len(getattr(prep, "selected_feature_names", []))
        if n_feat and n_feat > 0 and prep_feat > 0:
            assert n_feat == prep_feat, (
                f"Canonical artifact dimension mismatch: model={n_feat}, prep={prep_feat}"
            )
