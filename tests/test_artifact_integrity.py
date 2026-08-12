"""
SentinelAI Artifact Integrity & Schema Synchronization Tests
============================================================
Guarantees:
  - preprocessor.joblib output dimension matches best_model.joblib n_features_in_
  - artifact_manifest.json feature counts assert exact equality
  - real sample transformation and prediction executes without schema error
"""
import json
from pathlib import Path
import joblib
import numpy as np
import pytest

from ml.dataset.generator import CICIDS2017DataGenerator


def test_artifact_dimension_and_schema_synchronization():
    artifacts_dir = Path("ml/artifacts")
    prep_path = artifacts_dir / "preprocessor.joblib"
    model_path = artifacts_dir / "best_model.joblib"
    manifest_path = artifacts_dir / "artifact_manifest.json"

    assert prep_path.exists(), "preprocessor.joblib does not exist."
    assert model_path.exists(), "best_model.joblib does not exist."
    assert manifest_path.exists(), "artifact_manifest.json does not exist."

    preprocessor = joblib.load(prep_path)
    model_wrapper = joblib.load(model_path)
    inner_model = getattr(model_wrapper, "model", model_wrapper)

    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    # 1. Verify preprocessor selected features count
    selected_features = getattr(preprocessor, "selected_feature_names", [])
    assert len(selected_features) > 0, "Preprocessor has no selected features."

    # 2. Verify model n_features_in_
    n_features_in = getattr(inner_model, "n_features_in_", None)
    if n_features_in is not None:
        assert len(selected_features) == n_features_in, (
            f"MODEL_PREPROCESSOR_SCHEMA_MISMATCH: Preprocessor produces {len(selected_features)} "
            f"features but model expects {n_features_in}."
        )

    # 3. Assert manifest fields
    assert manifest["processed_feature_count"] == len(selected_features)
    if n_features_in is not None:
        assert manifest["model_n_features_in"] == n_features_in

    # 4. Perform real sample transformation and prediction
    generator = CICIDS2017DataGenerator()
    df_raw = generator.generate_synthetic_dataset(num_samples=5, random_seed=42)
    cleaned_df = preprocessor.clean_dataset(df_raw)
    X_raw = cleaned_df.drop(columns=["Label"])

    transformed_sample = preprocessor.transform_test(X_raw)
    assert transformed_sample.shape[1] == len(selected_features)

    preds = model_wrapper.predict(transformed_sample)
    assert len(preds) == 5
