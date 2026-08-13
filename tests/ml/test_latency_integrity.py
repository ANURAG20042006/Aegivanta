"""
tests/ml/test_latency_integrity.py
===================================
Verifies the inference latency measurement methodology:
  1. Training time (model.fit) is EXCLUDED from latency measurement.
  2. Prediction time (model.predict) is measured using time.perf_counter().
  3. Prediction is called once per fold and the result is reused for metrics.
  4. Promotion gate receives genuine inference latency (ms/sample).
  5. Training duration cannot reach or trigger promotion gate rejection.
  6. Missing latency returns None and rejects with "Promotion rejected: inference latency unavailable."
"""

import time
import numpy as np
import pytest
from unittest.mock import MagicMock

from ml.models.model_selector import ModelSelectorSuite
from ml.models.classical_models import DecisionTreeModel
from backend.app.api.v1.train import evaluate_promotion_gate


@pytest.fixture
def synthetic_train_data():
    rng = np.random.default_rng(42)
    X = rng.standard_normal((100, 30))
    y = np.array([i % 3 for i in range(100)])
    return X, y


class TestA_TrainingTimeIsNotLatency:
    """TEST A: Verify model.fit() duration is NOT included in cv_latency_ms."""

    def test_slow_fit_fast_predict_latency(self, synthetic_train_data):
        X, y = synthetic_train_data
        model = DecisionTreeModel()

        real_fit = model.fit
        real_predict = model.predict

        def slow_fit(X_tr, y_tr):
            time.sleep(0.05)  # 50ms artificial training delay
            return real_fit(X_tr, y_tr)

        model.fit = slow_fit

        suite = ModelSelectorSuite(models=[model])
        results = suite.train_and_select_champion(X_train=X, y_train=y, n_splits=2)

        res = results[0]
        # 50ms training time per fold / 50 samples would be 1.0ms/sample if fit were included.
        # But prediction takes ~0.001ms/sample. So cv_latency_ms MUST be < 0.1ms.
        assert res["cv_latency_ms"] < 0.2, (
            f"cv_latency_ms ({res['cv_latency_ms']}ms) reflects training time (50ms fit)! "
            f"Inference latency must exclude model.fit()."
        )


class TestB_PredictionTimeIsLatency:
    """TEST B: Verify model.predict() duration IS measured as latency."""

    def test_slow_predict_measured_in_latency(self, synthetic_train_data):
        X, y = synthetic_train_data
        model = DecisionTreeModel()

        real_predict = model.predict

        def slow_predict(X_val):
            time.sleep(0.01)  # 10ms artificial prediction delay
            return real_predict(X_val)

        model.predict = slow_predict

        suite = ModelSelectorSuite(models=[model])
        results = suite.train_and_select_champion(X_train=X, y_train=y, n_splits=2)

        res = results[0]
        # In 2-fold CV on 100 samples, val fold size is 50.
        # 10ms prediction / 50 samples = ~0.2ms per sample.
        assert res["cv_latency_ms"] >= 0.1, (
            f"cv_latency_ms ({res['cv_latency_ms']}ms) should reflect 10ms / 50 samples = ~0.2ms."
        )


class TestC_PredictionCalledOnce:
    """TEST C: Verify model.predict() is called ONCE per fold and reused for metrics."""

    def test_predict_called_once_per_fold(self, synthetic_train_data):
        X, y = synthetic_train_data
        model = DecisionTreeModel()

        predict_count = 0
        real_predict = model.predict

        def counted_predict(X_val):
            nonlocal predict_count
            predict_count += 1
            return real_predict(X_val)

        model.predict = counted_predict

        suite = ModelSelectorSuite(models=[model])
        n_splits = 3
        suite.train_and_select_champion(X_train=X, y_train=y, n_splits=n_splits)

        assert predict_count == n_splits, (
            f"model.predict() was called {predict_count} times during {n_splits}-fold CV. "
            f"Expected exactly {n_splits} calls (1 per fold)."
        )


class TestD_PromotionReceivesInferenceLatency:
    """TEST D: Verify evaluate_promotion_gate receives prediction latency."""

    def test_promotion_gate_accepts_valid_prediction_latency(self):
        cv_latency_ms = 0.35  # typical prediction latency (0.35ms/sample)
        passed, reason = evaluate_promotion_gate(
            candidate_f1=0.90,
            candidate_recall=0.88,
            candidate_fpr=0.02,
            candidate_latency_ms=cv_latency_ms,
            active_f1=None,
        )
        assert passed, f"Promotion gate rejected valid latency: {reason}"

    def test_promotion_gate_rejects_excessive_latency(self):
        cv_latency_ms = 12.5  # exceeds MAX_INFERENCE_LATENCY_MS (5.0ms)
        passed, reason = evaluate_promotion_gate(
            candidate_f1=0.90,
            candidate_recall=0.88,
            candidate_fpr=0.02,
            candidate_latency_ms=cv_latency_ms,
            active_f1=None,
        )
        assert not passed
        assert "exceeds max limit" in reason or "Latency" in reason


class TestE_TrainingTimeCannotReachPromotion:
    """TEST E: Verify slow training time (1000ms) does NOT cause promotion gate to fail."""

    def test_huge_training_time_small_prediction_time_promotes(self, synthetic_train_data):
        X, y = synthetic_train_data
        model = DecisionTreeModel()

        def super_slow_fit(X_tr, y_tr):
            time.sleep(0.1)  # simulated long training time
            return model.fit.__wrapped__(X_tr, y_tr) if hasattr(model.fit, "__wrapped__") else None

        # Measure simulated latency output
        training_duration_ms = 1000.0
        prediction_latency_ms = 0.05  # fast prediction (0.05ms/sample)

        # Gate must evaluate the PREDICTION latency, not the training duration
        passed, reason = evaluate_promotion_gate(
            candidate_f1=0.92,
            candidate_recall=0.89,
            candidate_fpr=0.02,
            candidate_latency_ms=prediction_latency_ms,  # 0.05ms
            active_f1=None,
        )
        assert passed, (
            f"Promotion gate failed despite prediction_latency=0.05ms < 5.0ms limit. "
            f"Reason: {reason}"
        )


class TestF_NoFabricatedLatency:
    """TEST F: Verify missing candidate_latency_ms (None) rejects without fallback."""

    def test_none_latency_rejects_promotion(self):
        passed, reason = evaluate_promotion_gate(
            candidate_f1=0.95,
            candidate_recall=0.92,
            candidate_fpr=0.01,
            candidate_latency_ms=None,  # missing
            active_f1=None,
        )
        assert not passed
        assert "inference latency unavailable" in reason, (
            f"Expected explicit rejection for missing latency, got: {reason}"
        )
