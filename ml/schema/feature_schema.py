import hashlib
import json
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field


class FeatureSchemaContract(BaseModel):
    """
    Formal schema contract defining feature names, ordering, dtypes,
    validation bounds, schema versioning, and missing-value policy.
    """
    version: str = "schema-v1.0"
    feature_names: List[str]
    required_features: List[str]
    optional_features: List[str] = Field(default_factory=list)
    dtypes: Dict[str, str]
    missing_value_policy: str = "median_impute_with_zero_fallback"
    
    def get_schema_hash(self) -> str:
        payload = json.dumps({
            "version": self.version,
            "feature_names": self.feature_names,
            "dtypes": self.dtypes
        }, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# Canonical 16 core features used in real-time vector inference
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

DEFAULT_FEATURE_SCHEMA = FeatureSchemaContract(
    version="schema-v1.0",
    feature_names=CANONICAL_FEATURES,
    required_features=["Destination Port", "Flow Duration", "Flow Packets/s", "Packet Length Mean"],
    optional_features=[f for f in CANONICAL_FEATURES if f not in ["Destination Port", "Flow Duration", "Flow Packets/s", "Packet Length Mean"]],
    dtypes=CANONICAL_DTYPES
)


def validate_input_vector(sample_dict: Dict[str, Any], schema: FeatureSchemaContract = DEFAULT_FEATURE_SCHEMA) -> Tuple[bool, List[str]]:
    """
    Validates an incoming packet feature dictionary against the feature schema contract.
    Returns (is_valid, list_of_errors).
    """
    errors = []
    for req in schema.required_features:
        if req not in sample_dict and req.lower().replace(" ", "_") not in sample_dict:
            # Check snake_case mapping fallback
            snake_name = req.lower().replace(" ", "_")
            if snake_name not in sample_dict:
                errors.append(f"Missing required feature: '{req}'")

    for key, val in sample_dict.items():
        if val is not None and not isinstance(val, (int, float, str, bool)):
            errors.append(f"Invalid data type for feature '{key}': {type(val).__name__}")
            
    return (len(errors) == 0, errors)
