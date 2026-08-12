import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, GradientBoostingClassifier
from ml.models.base_model import BaseSentinelModel

# Try importing XGBoost
try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

# Try importing LightGBM
try:
    from lightgbm import LGBMClassifier
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False

# Try importing CatBoost
try:
    from catboost import CatBoostClassifier
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False


class XGBoostModel(BaseSentinelModel):
    """Extreme Gradient Boosting Classifier."""

    def __init__(self, n_estimators: int = 100, learning_rate: float = 0.1):
        super().__init__(model_name="XGBoost", model_type="Boosting")
        if HAS_XGB:
            self.model = XGBClassifier(
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                random_state=42,
                eval_metric="mlogloss",
                n_jobs=-1
            )
        else:
            self.model = HistGradientBoostingClassifier(random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)


class LightGBMModel(BaseSentinelModel):
    """Light Gradient Boosting Machine Classifier."""

    def __init__(self, n_estimators: int = 100, learning_rate: float = 0.1):
        super().__init__(model_name="LightGBM", model_type="Boosting")
        if HAS_LGBM:
            self.model = LGBMClassifier(
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                random_state=42,
                verbose=-1,
                n_jobs=-1
            )
        else:
            self.model = HistGradientBoostingClassifier(random_state=43)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)


class CatBoostModel(BaseSentinelModel):
    """CatBoost Categorical Gradient Boosting Classifier."""

    def __init__(self, iterations: int = 100, learning_rate: float = 0.1):
        super().__init__(model_name="CatBoost", model_type="Boosting")
        if HAS_CATBOOST:
            self.model = CatBoostClassifier(
                iterations=iterations,
                learning_rate=learning_rate,
                random_seed=42,
                verbose=0
            )
        else:
            self.model = GradientBoostingClassifier(n_estimators=50, random_state=44)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        preds = self.model.predict(X)
        return np.asarray(preds).ravel()

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)
