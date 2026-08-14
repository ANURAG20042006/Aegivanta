"""
backend/app/schemas/alert.py
============================
Pydantic v2 validation schemas for Security Alerts.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


VALID_ALERT_STATUSES = ["new", "acknowledged", "investigating", "resolved", "dismissed"]
VALID_ALERT_SEVERITIES = ["info", "low", "medium", "high", "critical"]


class AlertStatusUpdate(BaseModel):
    status: str = Field(..., description="new, acknowledged, investigating, resolved, dismissed")
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        clean = v.lower().strip()
        if clean not in VALID_ALERT_STATUSES:
            raise ValueError(f"Invalid alert status. Must be one of: {VALID_ALERT_STATUSES}")
        return clean


from pydantic import BaseModel, Field, field_validator, ConfigDict


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    alert_id: str
    asset_id: Optional[str] = None
    incident_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    severity: str
    confidence: Optional[float] = None
    risk_score: float
    source: str
    source_ip: str
    destination_ip: str
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: str
    attack_type: str
    status: str
    explanation: Optional[Dict[str, Any]] = None
    timestamp: datetime
    created_at: datetime
    updated_at: datetime


class AlertListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[AlertResponse]


class AlertStatsResponse(BaseModel):
    total_active_alerts: int
    critical_alerts_count: int
    high_alerts_count: int
    new_alerts_count: int
    alerts_last_hour: int
    severity_breakdown: Dict[str, int]
