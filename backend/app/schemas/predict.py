from datetime import datetime
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class PacketFeatureVector(BaseModel):
    """Network flow feature schema based on CICIDS2017 specification."""
    source_ip: str = Field(default="192.168.1.105")
    destination_ip: str = Field(default="10.0.0.1")
    source_port: int = Field(default=443)
    destination_port: int = Field(default=80)
    protocol: str = Field(default="TCP")
    flow_duration: float = Field(default=120500.0)
    total_fwd_packets: float = Field(default=10.0)
    total_backward_packets: float = Field(default=8.0)
    packet_length_mean: float = Field(default=512.0)
    packet_length_std: float = Field(default=128.0)
    flow_bytes_s: float = Field(default=10240.0)
    flow_packets_s: float = Field(default=150.0)
    syn_flag_count: float = Field(default=1.0)
    rst_flag_count: float = Field(default=0.0)
    psh_flag_count: float = Field(default=1.0)
    ack_flag_count: float = Field(default=1.0)
    urg_flag_count: float = Field(default=0.0)
    # Allows callers with the complete CICIDS2017 payload to provide any additional
    # training features without breaking the compact UI vector contract.
    extra_features: Dict[str, float] = Field(default_factory=dict)


class PredictRequest(BaseModel):
    """Payload for single packet threat inference."""
    features: PacketFeatureVector
    model_name: Literal[
        "Random Forest", "XGBoost", "LightGBM", "CatBoost", "Decision Tree",
        "Logistic Regression", "SVM", "KNN", "Naive Bayes", "1D-CNN", "LSTM", "Autoencoder"
    ] = Field(default="Random Forest")


class PredictionResult(BaseModel):
    """Prediction output schema for a single inspected network flow."""
    incident_id: str
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    attack_type: str
    confidence_score: float
    is_malicious: bool
    severity: str
    model_used: str
    timestamp: datetime
    attack_probabilities: Dict[str, float]
    shap_explanation: Optional[Dict[str, float]] = None


class BatchPredictionResponse(BaseModel):
    """Response schema for batch CSV file predictions."""
    total_packets_inspected: int
    malicious_packets_count: int
    benign_packets_count: int
    threat_ratio_percentage: float
    results: List[PredictionResult]
