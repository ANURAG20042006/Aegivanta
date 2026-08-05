import joblib
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseSentinelModel(ABC):
    """Abstract Base Class for all SentinelAI Machine Learning & Deep Learning classifiers."""

    def __init__(self, model_name: str, model_type: str):
        self.model_name = model_name
        self.model_type = model_type  # Classical, Boosting, DeepLearning
        self.is_trained: bool = False
        self.model = None

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fits classifier model on training feature matrix X and target label array y."""
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predicts attack class indices for input feature matrix X."""
        pass

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predicts attack class probability distributions for input feature matrix X."""
        pass

    def save(self, filepath: str) -> None:
        """Serializes trained model artifact to disk."""
        joblib.dump(self.model, filepath)

    def load(self, filepath: str) -> None:
        """Loads serialized model artifact from disk."""
        self.model = joblib.load(filepath)
        self.is_trained = True
