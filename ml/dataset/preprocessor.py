import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any, Optional
from sklearn.model_selection import train_test_split
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
    - Splitting occurs BEFORE fitting scaling, feature selection, or class balancing.
    - StandardScaler & SelectKBest fit ONLY on X_train.
    - SMOTE is applied ONLY on X_train folds/splits, NEVER on X_test.
    """

    def __init__(self, n_features_to_select: int = 30):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_selector = SelectKBest(score_func=f_classif, k=n_features_to_select)
        self.n_features_to_select = n_features_to_select
        self.feature_names: List[str] = []
        self.selected_feature_names: List[str] = []
        self.is_fitted: bool = False

    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handles missing values, infinite values, and strips duplicate whitespace in column names."""
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

        df = df.fillna(0)
        return df

    def fit_transform_train_test(
        self,
        df: pd.DataFrame,
        target_column: str = "Label",
        balance_data: bool = True,
        test_size: float = 0.20,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Leakage-Free Execution:
        1. Clean dataset.
        2. Split X, y into Train and Test splits FIRST.
        3. Fit scaler & feature selector ONLY on X_train.
        4. Transform X_train and X_test independently using fitted parameters.
        5. Apply SMOTE ONLY on X_train.
        """
        cleaned_df = self.clean_dataset(df)

        if target_column not in cleaned_df.columns:
            raise KeyError(f"Target column '{target_column}' not found in dataset.")

        X_raw = cleaned_df.drop(columns=[target_column])
        y_raw = cleaned_df[target_column]

        self.feature_names = list(X_raw.columns)

        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y_raw.astype(str))

        # STEP 1: TRAIN / TEST SPLIT FIRST (Untouched Test Set Rule)
        X_train_raw, X_test_raw, y_train_encoded, y_test = train_test_split(
            X_raw, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
        )

        # STEP 2: FIT PREPROCESSING ONLY ON X_TRAIN
        X_train_scaled = self.scaler.fit_transform(X_train_raw)
        
        # Adjust n_features_to_select if feature count is smaller
        actual_k = min(self.n_features_to_select, X_train_raw.shape[1])
        self.feature_selector.k = actual_k
        
        X_train_selected = self.feature_selector.fit_transform(X_train_scaled, y_train_encoded)
        selected_indices = self.feature_selector.get_support(indices=True)
        self.selected_feature_names = [self.feature_names[i] for i in selected_indices]

        # STEP 3: TRANSFORM UNTOUCHED TEST SET USING FITTED SCALER & SELECTOR
        X_test_scaled = self.scaler.transform(X_test_raw)
        X_test_selected = self.feature_selector.transform(X_test_scaled)

        # STEP 4: SMOTE CLASS BALANCING ONLY ON X_TRAIN
        if balance_data and HAS_SMOTE:
            try:
                # Determine min samples per class to set k_neighbors safely
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
            k = min(self.n_features_to_select, len(sample_dict))
            vals = [float(v) for v in list(sample_dict.values())[:k]]
            return np.array([vals])

        vector = []
        for feature in self.feature_names:
            # Map canonical or snake_case key
            snake_key = feature.lower().replace(" ", "_")
            val = sample_dict.get(feature, sample_dict.get(snake_key, 0.0))
            try:
                vector.append(float(val) if val is not None else 0.0)
            except (ValueError, TypeError):
                vector.append(0.0)

        arr = pd.DataFrame([vector], columns=self.feature_names)
        arr = arr.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        scaled_arr = self.scaler.transform(arr)
        selected_arr = self.feature_selector.transform(scaled_arr)
        return selected_arr
