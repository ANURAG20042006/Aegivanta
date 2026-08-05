import numpy as np
import pandas as pd
from typing import Tuple, List, Dict
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_classif
try:
    from imblearn.over_sampling import SMOTE
    HAS_SMOTE = True
except ImportError:
    HAS_SMOTE = False

from ml.dataset.cicids2017_schema import CICIDS2017_FEATURES, ATTACK_CLASSES, LABEL_TO_INT


class CICIDS2017Preprocessor:
    """Robust data preprocessing pipeline for cleaning, scaling, and balancing network traffic datasets."""

    def __init__(self, n_features_to_select: int = 30):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_selector = SelectKBest(score_func=f_classif, k=n_features_to_select)
        self.n_features_to_select = n_features_to_select
        self.feature_names: List[str] = []
        self.selected_feature_names: List[str] = []
        self.is_fitted: bool = False

    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handles missing values, infinite values, and strips duplicate whitespace columns."""
        df = df.copy()
        df.columns = df.columns.str.strip()

        # Drop metadata non-feature columns if present
        meta_cols = ["Source IP", "Destination IP", "Protocol", "Timestamp"]
        for col in meta_cols:
            if col in df.columns:
                df = df.drop(columns=[col])

        # Replace infinite values with NaN
        df = df.replace([np.inf, -np.inf], np.nan)

        # Fill numerical NaNs with column median
        num_cols = df.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].median())

        # If any NaNs remain, fill with 0
        df = df.fillna(0)
        return df

    def fit_transform(
        self,
        df: pd.DataFrame,
        target_column: str = "Label",
        balance_data: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Preprocesses raw DataFrame, scales features, balances classes, and returns train/test splits."""
        cleaned_df = self.clean_dataset(df)

        if target_column not in cleaned_df.columns:
            raise KeyError(f"Target column '{target_column}' not found in dataset.")

        X_raw = cleaned_df.drop(columns=[target_column])
        y_raw = cleaned_df[target_column]

        self.feature_names = list(X_raw.columns)

        # Fit & transform labels
        y_encoded = self.label_encoder.fit_transform(y_raw.astype(str))

        # Scale features
        X_scaled = self.scaler.fit_transform(X_raw)

        # Feature selection
        X_selected = self.feature_selector.fit_transform(X_scaled, y_encoded)
        selected_indices = self.feature_selector.get_support(indices=True)
        self.selected_feature_names = [self.feature_names[i] for i in selected_indices]

        # Balance classes using SMOTE if enabled and installed
        if balance_data and HAS_SMOTE:
            try:
                smote = SMOTE(k_neighbors=1, random_state=42)
                X_resampled, y_resampled = smote.fit_resample(X_selected, y_encoded)
            except Exception:
                X_resampled, y_resampled = X_selected, y_encoded
        else:
            X_resampled, y_resampled = X_selected, y_encoded

        # Train/Test Split (80% Train, 20% Test)
        X_train, X_test, y_train, y_test = train_test_split(
            X_resampled, y_resampled, test_size=0.20, random_state=42, stratify=y_resampled
        )

        self.is_fitted = True
        return X_train, X_test, y_train, y_test

    def transform_sample(self, sample_dict: Dict[str, float]) -> np.ndarray:
        """Transforms a single feature dictionary for real-time model inference."""
        if not self.is_fitted:
            # Fallback scaling if transform called prior to fit
            vec = np.array([list(sample_dict.values())[:self.n_features_to_select]])
            return vec

        # Reconstruct vector in feature order
        vector = []
        for feature in self.feature_names:
            val = sample_dict.get(feature, 0.0)
            vector.append(val)

        arr = pd.DataFrame([vector], columns=self.feature_names)
        arr = arr.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        scaled_arr = self.scaler.transform(arr)
        selected_arr = self.feature_selector.transform(scaled_arr)
        return selected_arr
