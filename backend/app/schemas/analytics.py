from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class AttackDistributionItem(BaseModel):
    """Attack type summary item."""
    attack_type: str
    count: int
    percentage: float


class ModelPerformanceItem(BaseModel):
    """Model benchmark summary item."""
    model_name: str
    model_type: str
    accuracy: float
    f1_score: float
    precision_score: float
    recall_score: float
    roc_auc: Optional[float] = None
    is_active: bool


class AnalyticsSummary(BaseModel):
    """Dashboard analytics overview response."""
    network_status: str  # SECURE, WARNING, CRITICAL
    total_packets_inspected: int
    total_threats_detected: int
    critical_incidents_count: int
    prediction_accuracy: float
    active_model: str
    attack_distribution: List[AttackDistributionItem]
    model_performance: List[ModelPerformanceItem]
    top_source_ips: List[Dict[str, Any]]
    recent_incidents: List[Dict[str, Any]]
