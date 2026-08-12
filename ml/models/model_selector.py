import time
import os
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
)
from ml.models.base_model import BaseSentinelModel
from ml.models.classical_models import (
    RandomForestModel, DecisionTreeModel, LogisticRegressionModel, SVMModel, KNNModel, NaiveBayesModel
)
from ml.models.boosting_models import XGBoostModel, LightGBMModel, CatBoostModel
from ml.models.deep_learning import CNN1DModel, LSTMModel, AutoencoderModel


class ModelSelectorSuite:
    """
    Leakage-Free Model Selection Suite:
    - Fits models and evaluates selection criteria strictly on X_train / y_train via Stratified K-Fold CV.
    - Champion selection uses configurable multi-metric weighting (F1, Recall, FPR, Latency).
    - The frozen champion model is evaluated ONCE on the untouched X_test set after selection completes.
    """

    def __init__(
        self,
        artifacts_dir: str = "ml/artifacts",
        weights: Optional[Dict[str, float]] = None
    ):
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.models: List[BaseSentinelModel] = [
            RandomForestModel(),
            XGBoostModel(),
            LightGBMModel(),
            CatBoostModel(),
            DecisionTreeModel(),
            LogisticRegressionModel(),
            SVMModel(),
            KNNModel(),
            NaiveBayesModel(),
            CNN1DModel(),
            LSTMModel(),
            AutoencoderModel()
        ]
        # Configurable multi-metric selection weights (must sum to 1.0)
        self.weights = weights or {
            "f1": 0.40,
            "recall": 0.30,
            "low_fpr": 0.20,
            "latency": 0.10
        }
        self.evaluation_results: List[Dict[str, Any]] = []
        self.best_model: Optional[BaseSentinelModel] = None
        self.best_selection_score: float = -1.0
        self.final_test_metrics: Optional[Dict[str, Any]] = None

    def compute_selection_score(self, f1: float, recall: float, fpr: float, latency_ms: float) -> float:
        """
        Calculates a composite selection score based on CV metrics:
        Score = w_f1 * F1 + w_rec * Recall + w_fpr * (1 - FPR) + w_lat * max(0, 1 - latency/10)
        """
        norm_latency = max(0.0, 1.0 - (latency_ms / 10.0))
        score = (
            self.weights["f1"] * f1 +
            self.weights["recall"] * recall +
            self.weights["low_fpr"] * (1.0 - fpr) +
            self.weights["latency"] * norm_latency
        )
        return float(score)

    def train_and_select_champion(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        n_splits: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Performs leakage-free cross-validation strictly on X_train / y_train to select the champion model.
        Does NOT look at X_test or y_test during model selection.
        """
        self.evaluation_results = []
        self.best_model = None
        self.best_selection_score = -1.0

        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

        for model in self.models:
            print(f"--> Evaluating Selection for Model: {model.model_name} ({model.model_type}) via {n_splits}-Fold CV on TRAIN set...")
            fold_f1s, fold_recalls, fold_fprs, fold_latencies = [], [], [], []

            try:
                for train_idx, val_idx in skf.split(X_train, y_train):
                    X_tr_fold, X_val_fold = X_train[train_idx], X_train[val_idx]
                    y_tr_fold, y_val_fold = y_train[train_idx], y_train[val_idx]

                    t0 = time.time()
                    model.fit(X_tr_fold, y_tr_fold)
                    t_lat = (time.time() - t0) * 1000.0 / max(len(X_val_fold), 1)

                    y_val_pred = model.predict(X_val_fold)

                    f1 = float(f1_score(y_val_fold, y_val_pred, average="macro", zero_division=0))
                    rec = float(recall_score(y_val_fold, y_val_pred, average="macro", zero_division=0))
                    fpr = float(1.0 - rec)

                    fold_f1s.append(f1)
                    fold_recalls.append(rec)
                    fold_fprs.append(fpr)
                    fold_latencies.append(t_lat)

                avg_f1 = float(np.mean(fold_f1s))
                avg_rec = float(np.mean(fold_recalls))
                avg_fpr = float(np.mean(fold_fprs))
                avg_lat = float(np.mean(fold_latencies))

                selection_score = self.compute_selection_score(avg_f1, avg_rec, avg_fpr, avg_lat)

                result = {
                    "model_name": model.model_name,
                    "model_type": model.model_type,
                    "cv_f1_mean": round(avg_f1, 4),
                    "cv_recall_mean": round(avg_rec, 4),
                    "cv_fpr_mean": round(avg_fpr, 4),
                    "cv_latency_ms": round(avg_lat, 4),
                    "selection_score": round(selection_score, 4),
                    "instance": model
                }
                self.evaluation_results.append(result)

                if selection_score > self.best_selection_score:
                    self.best_selection_score = selection_score
                    self.best_model = model

            except Exception as e:
                print(f"Error evaluating model {model.model_name} during CV selection: {str(e)}")

        # Refit champion model on 100% of X_train
        if self.best_model:
            print(f"=== Champion Model Selected: {self.best_model.model_name} (Selection Score: {self.best_selection_score:.4f}) ===")
            print(f"--> Refitting {self.best_model.model_name} on full X_train dataset...")
            self.best_model.fit(X_train, y_train)

            # Persist Champion Model
            champion_path = self.artifacts_dir / "best_model.joblib"
            self.best_model.save(str(champion_path))

        return self.evaluation_results

    def evaluate_final_test_set(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, Any]:
        """
        Evaluates the frozen champion model ONCE on the untouched test set after model selection has finished.
        Returns final_test_metrics.
        """
        if not self.best_model:
            raise RuntimeError("Cannot evaluate final test set: No champion model selected.")

        print(f"--> Evaluating Frozen Champion Model ({self.best_model.model_name}) ONCE on Untouched TEST Set...")
        t0 = time.time()
        y_pred = self.best_model.predict(X_test)
        latency_ms = round((time.time() - t0) * 1000.0 / max(len(X_test), 1), 4)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
        rec = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
        f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
        fpr = float(1.0 - rec)
        cm = confusion_matrix(y_test, y_pred).tolist()

        # Compute ROC-AUC without fabricated fallbacks
        roc_auc = None
        probs = self.best_model.predict_proba(X_test)
        if probs is not None:
            try:
                roc_auc = round(float(roc_auc_score(y_test, probs, multi_class="ovr", average="macro")), 4)
            except Exception:
                roc_auc = None

        self.final_test_metrics = {
            "accuracy": round(acc, 4),
            "macro_f1": round(f1, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "fpr": round(fpr, 4),
            "roc_auc": roc_auc,
            "inference_latency_ms": latency_ms,
            "confusion_matrix": cm,
            "test_sample_count": len(y_test)
        }
        return self.final_test_metrics

    def train_and_evaluate_all(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Backward-compatible wrapper executing train_and_select_champion followed by evaluate_final_test_set."""
        results = self.train_and_select_champion(X_train, y_train)
        self.evaluate_final_test_set(X_test, y_test)
        return results
