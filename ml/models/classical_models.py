import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from ml.models.base_model import BaseSentinelModel


class RandomForestModel(BaseSentinelModel):
    """Random Forest Classifier for robust ensemble network packet threat classification."""

    def __init__(self, n_estimators: int = 100, max_depth: int = 20):
        super().__init__(model_name="Random Forest", model_type="Classical")
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)


class DecisionTreeModel(BaseSentinelModel):
    """Decision Tree Classifier."""

    def __init__(self, max_depth: int = 15):
        super().__init__(model_name="Decision Tree", model_type="Classical")
        self.model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)


class LogisticRegressionModel(BaseSentinelModel):
    """Logistic Regression Classifier."""

    def __init__(self):
        super().__init__(model_name="Logistic Regression", model_type="Classical")
        self.model = LogisticRegression(max_iter=1000, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)


class SVMModel(BaseSentinelModel):
    """Support Vector Machine Classifier."""

    def __init__(self):
        super().__init__(model_name="SVM", model_type="Classical")
        self.model = SVC(probability=True, kernel='rbf', random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)


class KNNModel(BaseSentinelModel):
    """K-Nearest Neighbors Classifier."""

    def __init__(self, n_neighbors: int = 5):
        super().__init__(model_name="KNN", model_type="Classical")
        self.model = KNeighborsClassifier(n_neighbors=n_neighbors, n_jobs=-1)

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)


class NaiveBayesModel(BaseSentinelModel):
    """Gaussian Naive Bayes Classifier."""

    def __init__(self):
        super().__init__(model_name="Naive Bayes", model_type="Classical")
        self.model = GaussianNB()

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)
