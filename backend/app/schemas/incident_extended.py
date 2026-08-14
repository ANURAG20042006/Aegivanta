from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.alert import AlertResponse
from backend.app.schemas.asset import AssetResponse


class TimelineEventCreate(BaseModel):
    event_type: str = Field("ANALYST_ACTION", description="DETECTION, ALERT_CORRELATED, TRIAGE, STATUS_CHANGE, ANALYST_ACTION, REMEDIATION, RESOLUTION")
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    metadata_payload: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TimelineEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    timestamp: datetime
    event_type: str
    title: str
    description: Optional[str] = None
    actor: str
    metadata_payload: Optional[Dict[str, Any]] = None


class IncidentDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_code: str
    alert_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    status: str
    risk_score: float
    alert_count: int
    severity: str
    attack_type: str
    confidence_score: Optional[float] = None
    is_malicious: bool
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    model_name: str
    model_version: str
    analyst: Optional[str] = None
    notes: Optional[str] = None
    resolution: Optional[str] = None
    remediation_action: Optional[str] = None
    timestamp: datetime
    first_seen: datetime
    last_seen: datetime
    triaged_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    asset: Optional[AssetResponse] = None
    alerts: List[AlertResponse] = []
    timeline: List[TimelineEventResponse] = []
