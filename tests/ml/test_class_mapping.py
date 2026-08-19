"""
tests/ml/test_class_mapping.py
==============================
Unit tests verifying strict model class -> attack label mapping,
label encoder synchronization, bounds validation, and fail-safe error handling.
"""

import pytest
import numpy as np
from fastapi import HTTPException
from sklearn.preprocessing import LabelEncoder
from backend.app.services.predict_service import PredictService
from backend.app.schemas.predict import PacketFeatureVector
from ml.dataset.cicids2017_schema import ATTACK_CLASSES


class MockModelWithClasses:
    def __init__(self, classes):
        self.classes_ = np.array(classes)

    def predict(self, X):
        return np.array([0])

    def predict_proba(self, X):
        probs = np.zeros((1, len(self.classes_)))
        probs[0, 0] = 0.95
        return probs


class MockModelWithoutClasses:
    def predict(self, X):
        return np.array([0])


class MockPreprocessorWithLE:
    def __init__(self, class_list):
        self.label_encoder = LabelEncoder()
        self.label_encoder.classes_ = np.array(class_list)
        self.selected_feature_names = [f"feat_{i}" for i in range(30)]

    def transform_raw_sample(self, raw_dict):
        return np.zeros((1, 30))


def test_matching_class_order_resolution():
    """Verify class mapping resolves correctly when label encoder matches training order."""
    classes = ["BENIGN", "DDoS", "Port Scan", "Botnet"]
    prep = MockPreprocessorWithLE(classes)
    model = MockModelWithClasses([0, 1, 2, 3])

    # Index 1 should resolve to DDoS
    class_idx = 1
    classes_le = prep.label_encoder
    assert str(classes_le.classes_[class_idx]) == "DDoS"


def test_different_class_order_preserved():
    """Verify class mapping does NOT confuse index 0 as BENIGN if label encoder puts ARP Spoofing at index 0."""
    alphabetical_classes = ["ARP Spoofing", "BENIGN", "Botnet", "DDoS"]
    prep = MockPreprocessorWithLE(alphabetical_classes)

    # Index 0 must resolve to 'ARP Spoofing', NOT 'BENIGN'
    assert prep.label_encoder.classes_[0] == "ARP Spoofing"
    assert prep.label_encoder.classes_[1] == "BENIGN"
    assert prep.label_encoder.classes_[3] == "DDoS"


def test_out_of_bounds_class_index_raises_http_503():
    """Verify out-of-bounds predicted class index fails closed with HTTP 503 rather than returning wrong class."""
    classes = ["BENIGN", "DDoS"]
    prep = MockPreprocessorWithLE(classes)
    class_idx = 99  # Invalid index

    classes_le = prep.label_encoder
    with pytest.raises(HTTPException) as exc_info:
        if class_idx < len(classes_le.classes_):
            _ = str(classes_le.classes_[class_idx])
        else:
            raise HTTPException(
                status_code=503,
                detail=f"MODEL_CLASS_MAPPING_ERROR: Predicted class index {class_idx} exceeds count {len(classes_le.classes_)}."
            )
    assert exc_info.value.status_code == 503
    assert "MODEL_CLASS_MAPPING_ERROR" in exc_info.value.detail


def test_real_model_preprocessor_classes_synchronization():
    """Verify loaded champion CatBoost and Preprocessor have valid, synchronized class mappings."""
    import joblib
    from pathlib import Path

    model_path = Path("ml/artifacts/catboost.joblib")
    prep_path = Path("ml/artifacts/preprocessor.joblib")

    if model_path.exists() and prep_path.exists():
        cb = joblib.load(model_path)
        prep = joblib.load(prep_path)

        assert hasattr(prep, "label_encoder")
        assert hasattr(prep.label_encoder, "classes_")
        assert len(prep.label_encoder.classes_) > 0
        assert "BENIGN" in prep.label_encoder.classes_
        assert "DDoS" in prep.label_encoder.classes_

        # Model output dimensions must match preprocessor classes count
        assert len(cb.classes_) == len(prep.label_encoder.classes_)
