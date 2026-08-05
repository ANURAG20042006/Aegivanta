import numpy as np
import pandas as pd
from typing import Tuple
from ml.dataset.cicids2017_schema import CICIDS2017_FEATURES, ATTACK_CLASSES


class CICIDS2017DataGenerator:
    """Generates synthetic high-fidelity benchmark datasets matching CICIDS2017 feature schemas."""

    @staticmethod
    def generate_synthetic_dataset(num_samples: int = 5000, random_seed: int = 42) -> pd.DataFrame:
        """Generates a synthetic DataFrame populated with realistic flow characteristics across 15 attack types."""
        np.random.seed(random_seed)

        data = {}
        # Generate 78 continuous/discrete network features
        for feature in CICIDS2017_FEATURES:
            if "Flags" in feature or "Count" in feature:
                data[feature] = np.random.choice([0, 1], size=num_samples, p=[0.85, 0.15])
            elif "Port" in feature:
                data[feature] = np.random.choice([80, 443, 21, 22, 53, 8080, 3389, 445], size=num_samples)
            elif "Bytes/s" in feature or "Packets/s" in feature:
                data[feature] = np.random.exponential(scale=5000.0, size=num_samples)
            elif "Duration" in feature or "IAT" in feature:
                data[feature] = np.random.gamma(shape=2.0, scale=10000.0, size=num_samples)
            else:
                data[feature] = np.random.normal(loc=150.0, scale=50.0, size=num_samples)

        # Inject periodic NaN and Inf to validate cleaning pipeline
        mask_nan = np.random.choice([True, False], size=num_samples, p=[0.01, 0.99])
        mask_inf = np.random.choice([True, False], size=num_samples, p=[0.01, 0.99])
        data["Flow Bytes/s"][mask_nan] = np.nan
        data["Flow Packets/s"][mask_inf] = np.inf

        # Generate attack labels with realistic class imbalance (BENIGN = 70%)
        attack_probabilities = [0.70] + [0.30 / (len(ATTACK_CLASSES) - 1)] * (len(ATTACK_CLASSES) - 1)
        # Normalize sum to 1.0
        attack_probabilities = np.array(attack_probabilities) / np.sum(attack_probabilities)
        data["Label"] = np.random.choice(ATTACK_CLASSES, size=num_samples, p=attack_probabilities)

        # Add IP and Metadata columns
        data["Source IP"] = [f"192.168.1.{np.random.randint(2, 254)}" for _ in range(num_samples)]
        data["Destination IP"] = ["10.0.0.1" for _ in range(num_samples)]
        data["Protocol"] = np.random.choice(["TCP", "UDP"], size=num_samples, p=[0.8, 0.2])

        df = pd.DataFrame(data)
        return df


if __name__ == "__main__":
    generator = CICIDS2017DataGenerator()
    df = generator.generate_synthetic_dataset(num_samples=1000)
    print(f"Generated synthetic dataset shape: {df.shape}")
    print(df["Label"].value_counts())
