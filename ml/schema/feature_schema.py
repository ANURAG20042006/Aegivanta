import hashlib
import json
from typing import Dict, Any, List, Tuple, Optional
from pydantic import BaseModel, Field


class FeatureSchemaContract(BaseModel):
    """
    Formal schema contract defining feature names, exact ordering, dtypes,
    allowed numerical ranges, schema versioning, and missing-value policy.
    """
    version: str = "schema-v1.0"
    feature_names: List[str]
    required_features: List[str]
    optional_features: List[str] = Field(default_factory=list)
    dtypes: Dict[str, str]
    allowed_ranges: Dict[str, Tuple[float, float]] = Field(default_factory=dict)
    missing_value_policy: str = "median_impute_with_zero_fallback"
    
    def get_schema_hash(self) -> str:
        payload = json.dumps({
            "version": self.version,
            "feature_names": self.feature_names,
            "dtypes": self.dtypes
        }, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# Canonical 16 core features used in real-time vector inference with exact ordering
CANONICAL_FEATURES: List[str] = [
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Packet Length Mean",
    "Packet Length Std",
    "SYN Flag Count",
    "RST Flag Count",
    "PSH Flag Count",
    "ACK Flag Count",
    "URG Flag Count",
    "Average Packet Size"
]

CANONICAL_DTYPES: Dict[str, str] = {feature: "float64" for feature in CANONICAL_FEATURES}

CANONICAL_RANGES: Dict[str, Tuple[float, float]] = {
    "Destination Port": (0.0, 65535.0),
    "Flow Duration": (0.0, 864000000.0),
    "Total Fwd Packets": (0.0, 10000000.0),
    "Total Backward Packets": (0.0, 10000000.0),
    "Flow Bytes/s": (0.0, 1e12),
    "Flow Packets/s": (0.0, 1e9),
    "Packet Length Mean": (0.0, 65535.0),
    "SYN Flag Count": (0.0, 100.0)
}

DEFAULT_FEATURE_SCHEMA = FeatureSchemaContract(
    version="schema-v1.0",
    feature_names=CANONICAL_FEATURES,
    required_features=["Destination Port", "Flow Duration", "Flow Packets/s", "Packet Length Mean", "SYN Flag Count"],
    optional_features=[f for f in CANONICAL_FEATURES if f not in ["Destination Port", "Flow Duration", "Flow Packets/s", "Packet Length Mean", "SYN Flag Count"]],
    dtypes=CANONICAL_DTYPES,
    allowed_ranges=CANONICAL_RANGES
)


def validate_input_vector(
    sample_dict: Dict[str, Any],
    schema: FeatureSchemaContract = DEFAULT_FEATURE_SCHEMA
) -> Tuple[bool, List[str]]:
    """
    Validates an incoming packet feature dictionary against the feature schema contract.
    Returns (is_valid, list_of_errors). Rejects missing required features, invalid dtypes, and out-of-range values.
    """
    errors = []

    # 1. Missing required features check
    for req in schema.required_features:
        snake_key = req.lower().replace(" ", "_").replace("/", "_")
        if req not in sample_dict and snake_key not in sample_dict:
            errors.append(f"Missing required feature: '{req}'")

    # 2. Data type and Range validation
    for key, val in sample_dict.items():
        if val is None:
            continue
        
        # Check invalid non-numeric data types (e.g. dict, list)
        if isinstance(val, (dict, list, tuple)):
            errors.append(f"Invalid data type for feature '{key}': {type(val).__name__}")
            continue

        try:
            num_val = float(val)
        except (ValueError, TypeError):
            errors.append(f"Invalid numeric value for feature '{key}': {val}")
            continue

        # Check allowed ranges where known
        for feature_name, (min_val, max_val) in schema.allowed_ranges.items():
            snake_name = feature_name.lower().replace(" ", "_").replace("/", "_")
            if key == feature_name or key == snake_name:
                if not (min_val <= num_val <= max_val):
                    errors.append(f"Feature '{key}' value {num_val} is out of allowed range [{min_val}, {max_val}]")

    return (len(errors) == 0, errors)


def validate_artifact_compatibility(
    metadata: Dict[str, Any],
    expected_schema_version: str = "schema-v1.0",
    expected_preprocessing_version: str = "split_first_smote_inside_folds_only"
) -> Tuple[bool, List[str]]:
    """
    Validates model artifact metadata integrity & compatibility before inference.
    Checks model_version, feature_schema_version, and preprocessing_version.
    """
    errors = []

    if not metadata:
        return False, ["Model artifact metadata is missing or empty."]

    schema_ver = metadata.get("feature_schema_version")
    if schema_ver != expected_schema_version:
        errors.append(f"Incompatible feature schema version '{schema_ver}' (expected '{expected_schema_version}')")

    prep_ver = metadata.get("preprocessing_version")
    if prep_ver != expected_preprocessing_version and prep_ver != "split_first_smote_train_only":
        errors.append(f"Incompatible preprocessing version '{prep_ver}' (expected '{expected_preprocessing_version}')")

    if not metadata.get("model_version"):
        errors.append("Model version missing from artifact metadata.")

    return (len(errors) == 0, errors)
