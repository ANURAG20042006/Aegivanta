import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any, Optional
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_classif
try:
    from imblearn.over_sampling import SMOTE
    HAS_SMOTE = True
except ImportError:
    HAS_SMOTE = False

from ml.dataset.cicids2017_schema import CICIDS2017_FEATURES, ATTACK_CLASSES, LABEL_TO_INT
from ml.schema.feature_schema import CANONICAL_FEATURES, DEFAULT_FEATURE_SCHEMA


class CICIDS2017Preprocessor:
    """
    Strict Leakage-Free Preprocessing Pipeline:
    - Splitting occurs BEFORE fitting imputation, scaling, feature selection, or class balancing.
    - SimpleImputer, StandardScaler & SelectKBest fit ONLY on X_train.
    - SMOTE is applied ONLY on X_train folds/splits, NEVER on validation or test sets.
    """

    def __init__(self, n_features_to_select: int = 30):
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_selector = SelectKBest(score_func=f_classif, k=n_features_to_select)
        self.n_features_to_select = n_features_to_select
        self.feature_names: List[str] = []
        self.selected_feature_names: List[str] = []
        self.is_fitted: bool = False

    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans column names, drops metadata columns, and replaces infinite values with NaN.
        NOTE: Does NOT compute column medians or fill NaNs globally across the full dataset,
        guaranteeing zero test-set leakage into imputation parameters.
        """
        df = df.copy()
        df.columns = df.columns.str.strip()

        # Drop metadata non-feature columns if present
        meta_cols = ["Source IP", "Destination IP", "Protocol", "Timestamp"]
        for col in meta_cols:
            if col in df.columns:
                df = df.drop(columns=[col])

        # Replace infinite values with NaN for downstream fitted imputer
        df = df.replace([np.inf, -np.inf], np.nan)
        return df

    def fit_transform_train(
        self,
        X_train_raw: Any,
        y_train_encoded: np.ndarray,
        balance_data: bool = True,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fits imputer, scaler, feature selector, and SMOTE strictly on training raw features only.
        """
        if isinstance(X_train_raw, pd.DataFrame):
            self.feature_names = list(X_train_raw.columns)
            X_tr_values = X_train_raw.values
        else:
            X_tr_values = np.asarray(X_train_raw)
            if not self.feature_names or len(self.feature_names) != X_tr_values.shape[1]:
                self.feature_names = [f"feature_{i}" for i in range(X_tr_values.shape[1])]

        # 1. Fit & transform SimpleImputer strictly on training split
        X_train_imputed = self.imputer.fit_transform(X_tr_values)

        # 2. Fit & transform StandardScaler strictly on training imputed data
        X_train_scaled = self.scaler.fit_transform(X_train_imputed)

        # 3. Fit & transform SelectKBest strictly on training scaled data
        if self.n_features_to_select is None:
            actual_k = "all"
        else:
            actual_k = min(self.n_features_to_select, X_tr_values.shape[1])
        self.feature_selector.k = actual_k

        X_train_selected = self.feature_selector.fit_transform(X_train_scaled, y_train_encoded)
        selected_indices = self.feature_selector.get_support(indices=True)
        self.selected_feature_names = [self.feature_names[i] for i in selected_indices]

        # 4. Apply SMOTE class balancing strictly on training selected data
        if balance_data and HAS_SMOTE:
            try:
                unique_classes, counts = np.unique(y_train_encoded, return_counts=True)
                min_class_samples = min(counts)
                k_neighbors = min(5, max(1, min_class_samples - 1))
                
                if k_neighbors >= 1:
                    smote = SMOTE(k_neighbors=k_neighbors, random_state=random_state)
                    X_train_final, y_train_final = smote.fit_resample(X_train_selected, y_train_encoded)
                else:
                    X_train_final, y_train_final = X_train_selected, y_train_encoded
            except Exception:
                X_train_final, y_train_final = X_train_selected, y_train_encoded
        else:
            X_train_final, y_train_final = X_train_selected, y_train_encoded

        self.is_fitted = True
        return X_train_final, y_train_final

    def transform_test(self, X_test_raw: Any) -> np.ndarray:
        """
        Transforms untouched test set using fitted imputer, scaler, and selector.
        Never applies SMOTE.
        """
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted on training data first.")

        if isinstance(X_test_raw, pd.DataFrame):
            X_te_values = X_test_raw.values
        else:
            X_te_values = np.asarray(X_test_raw)

        # Transform sequentially through fitted pipeline components
        X_test_imputed = self.imputer.transform(X_te_values)
        X_test_scaled = self.scaler.transform(X_test_imputed)
        X_test_selected = self.feature_selector.transform(X_test_scaled)
        return X_test_selected

    def fit_transform_train_test(
        self,
        df: pd.DataFrame,
        target_column: str = "Label",
        balance_data: bool = True,
        test_size: float = 0.20,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Leakage-Free Execution (Split-First):
        1. Clean column names & convert +/-inf to NaN.
        2. Split X, y into Train and Test splits FIRST before computing statistics.
        3. Fit imputer, scaler & feature selector ONLY on X_train.
        4. Transform X_train and X_test independently using fitted parameters.
        5. Apply SMOTE ONLY on X_train.
        """
        cleaned_df = self.clean_dataset(df)

        if target_column not in cleaned_df.columns:
            raise KeyError(f"Target column '{target_column}' not found in dataset.")

        X_raw = cleaned_df.drop(columns=[target_column])
        y_raw = cleaned_df[target_column]

        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y_raw.astype(str))

        # STEP 1: TRAIN / TEST SPLIT FIRST (Untouched Test Set Rule)
        X_train_raw, X_test_raw, y_train_encoded, y_test = train_test_split(
            X_raw, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
        )
        self.X_train_raw = X_train_raw.values if isinstance(X_train_raw, pd.DataFrame) else X_train_raw
        self.y_train_encoded = y_train_encoded

        # STEP 2 & 3 & 4: Process using decoupled methods
        X_train_final, y_train_final = self.fit_transform_train(
            X_train_raw, y_train_encoded, balance_data=balance_data, random_state=random_state
        )
        X_test_selected = self.transform_test(X_test_raw)

        return X_train_final, X_test_selected, y_train_final, y_test

    def fit_transform(
        self,
        df: pd.DataFrame,
        target_column: str = "Label",
        balance_data: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Backward-compatible entry point calling leakage-free pipeline."""
        return self.fit_transform_train_test(df, target_column=target_column, balance_data=balance_data)

    def transform_raw_sample(self, sample_dict: Dict[str, Any]) -> np.ndarray:
        """Transforms a single raw feature dictionary for production inference using fitted transformers."""
        if not self.is_fitted:
            # Fallback if un-fitted
            k = len(sample_dict) if self.n_features_to_select is None else min(self.n_features_to_select, len(sample_dict))
            vals = [float(v) for v in list(sample_dict.values())[:k]]
            return np.array([vals])

        extra_dict = sample_dict.get("extra_features", {}) if isinstance(sample_dict.get("extra_features"), dict) else {}
        vector = []
        for feature in self.feature_names:
            # Map canonical or snake_case key across root and extra_features
            snake_key = feature.lower().replace(" ", "_")
            val = sample_dict.get(
                feature,
                sample_dict.get(
                    snake_key,
                    extra_dict.get(feature, extra_dict.get(snake_key, np.nan))
                )
            )
            try:
                vector.append(float(val) if val is not None else np.nan)
            except (ValueError, TypeError):
                vector.append(np.nan)

        arr = np.array([vector], dtype=float)
        # Handle inf values in single inference vector
        arr = np.where(np.isneginf(arr) | np.isposinf(arr), np.nan, arr)
        
        imputed_arr = self.imputer.transform(arr)
        scaled_arr = self.scaler.transform(imputed_arr)
        selected_arr = self.feature_selector.transform(scaled_arr)
        return selected_arr

