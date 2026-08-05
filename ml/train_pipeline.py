import os
import joblib
import pandas as pd
from pathlib import Path
from ml.dataset.generator import CICIDS2017DataGenerator
from ml.dataset.preprocessor import CICIDS2017Preprocessor
from ml.models.model_selector import ModelSelectorSuite


def run_training_pipeline(
    dataset_path: str = None,
    num_synthetic_samples: int = 1500,
    artifacts_dir: str = "ml/artifacts"
):
    """
    End-to-End SentinelAI ML Training & Evaluation Pipeline:
    1. Loads or generates CICIDS2017 dataset.
    2. Cleans, scales, encodes, and balances dataset.
    3. Trains and evaluates all 12 ML/DL models.
    4. Auto-selects the best model based on F1-score.
    5. Serializes preprocessor and trained models to artifacts directory.
    """
    print("==========================================================")
    print("      SentinelAI Intelligent NIDS ML Training Engine      ")
    print("==========================================================")

    artifacts_path = Path(artifacts_dir)
    artifacts_path.mkdir(parents=True, exist_ok=True)

    # Step 1: Load or Generate Dataset
    if dataset_path and os.path.exists(dataset_path):
        print(f"--> Loading real CICIDS2017 dataset from: {dataset_path}")
        df = pd.read_csv(dataset_path)
    else:
        print(f"--> Generating synthetic CICIDS2017 benchmark dataset ({num_synthetic_samples} samples)...")
        df = CICIDS2017DataGenerator.generate_synthetic_dataset(num_samples=num_synthetic_samples)

    print(f"--> Dataset loaded successfully. Shape: {df.shape}")

    # Step 2: Data Preprocessing
    print("--> Preprocessing dataset (Cleaning, Scaling, SMOTE Balancing, Feature Selection)...")
    preprocessor = CICIDS2017Preprocessor(n_features_to_select=30)
    X_train, X_test, y_train, y_test = preprocessor.fit_transform(df, target_column="Label", balance_data=True)

    # Save Preprocessor Artifact
    preprocessor_path = artifacts_path / "preprocessor.joblib"
    joblib.dump(preprocessor, preprocessor_path)
    print(f"--> Preprocessor artifact saved to: {preprocessor_path}")

    # Step 3: Train & Compare All 12 Models
    print("--> Initializing Model Selector Suite across 12 ML & Deep Learning Classifiers...")
    selector = ModelSelectorSuite(artifacts_dir=artifacts_dir)
    results = selector.train_and_evaluate_all(X_train, y_train, X_test, y_test)

    # Print Summary Table
    print("\n==========================================================")
    print("                  MODEL COMPARISON LEADERBOARD            ")
    print("==========================================================")
    print(f"{'Model Name':<22} | {'Type':<12} | {'Accuracy':<8} | {'F1 Score':<8} | {'Precision':<8} | {'Time (s)':<8}")
    print("-" * 75)
    for res in results:
        print(
            f"{res['model_name']:<22} | "
            f"{res['model_type']:<12} | "
            f"{res['accuracy']:<8.4f} | "
            f"{res['f1_score']:<8.4f} | "
            f"{res['precision']:<8.4f} | "
            f"{res['training_time_sec']:<8.2f}"
        )
    print("==========================================================")

    if selector.best_model:
        print(f"SUCCESS: Best Model Selected & Exported: {selector.best_model.model_name}")
    return results


if __name__ == "__main__":
    run_training_pipeline()
