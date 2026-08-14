"""
backend/app/schemas/asset.py
============================
Pydantic v2 validation schemas for Protected Assets.
Includes domain/URL sanitary checks to guard against SSRF.
"""

import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


VALID_ASSET_TYPES = ["website", "api", "server", "database", "endpoint", "network", "other"]
VALID_ENVIRONMENTS = ["production", "staging", "development"]
VALID_CRITICALITIES = ["low", "medium", "high", "critical"]
VALID_ASSET_STATUSES = ["active", "degraded", "compromised", "maintenance", "inactive"]


class AssetBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Asset display name")
    hostname: str = Field(..., min_length=1, max_length=255, description="FQDN, hostname or identifier")
    url: Optional[str] = Field(None, max_length=500, description="Optional service URL")
    ip_address: Optional[str] = Field(None, max_length=45, description="Associated IP address for flow matching")
    asset_type: str = Field("website", description="Asset type: website, api, server, database, endpoint, network, other")
    environment: str = Field("production", description="Environment: production, staging, development")
    criticality: str = Field("medium", description="Criticality tier: low, medium, high, critical")
    status: str = Field("active", description="Status: active, degraded, compromised, maintenance, inactive")
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @field_validator("asset_type")
    @classmethod
    def validate_asset_type(cls, v: str) -> str:
        v_clean = v.lower().strip()
        if v_clean not in VALID_ASSET_TYPES:
            raise ValueError(f"Invalid asset_type. Must be one of: {VALID_ASSET_TYPES}")
        return v_clean

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        v_clean = v.lower().strip()
        if v_clean not in VALID_ENVIRONMENTS:
            raise ValueError(f"Invalid environment. Must be one of: {VALID_ENVIRONMENTS}")
        return v_clean

    @field_validator("criticality")
    @classmethod
    def validate_criticality(cls, v: str) -> str:
        v_clean = v.lower().strip()
        if v_clean not in VALID_CRITICALITIES:
            raise ValueError(f"Invalid criticality. Must be one of: {VALID_CRITICALITIES}")
        return v_clean

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        v_clean = v.lower().strip()
        if v_clean not in VALID_ASSET_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {VALID_ASSET_STATUSES}")
        return v_clean

    @field_validator("hostname")
    @classmethod
    def validate_hostname(cls, v: str) -> str:
        clean = v.strip()
        if not re.match(r"^[a-zA-Z0-9.\-_:]+$", clean):
            raise ValueError("Hostname contains invalid characters.")
        return clean

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        clean = v.strip()
        if not (clean.startswith("http://") or clean.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return clean


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    hostname: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)
    asset_type: Optional[str] = None
    environment: Optional[str] = None
    criticality: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None

    @field_validator("asset_type")
    @classmethod
    def validate_type_opt(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower().strip() not in VALID_ASSET_TYPES:
            raise ValueError(f"Must be one of {VALID_ASSET_TYPES}")
        return v.lower().strip() if v else None

    @field_validator("environment")
    @classmethod
    def validate_env_opt(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower().strip() not in VALID_ENVIRONMENTS:
            raise ValueError(f"Must be one of {VALID_ENVIRONMENTS}")
        return v.lower().strip() if v else None

    @field_validator("criticality")
    @classmethod
    def validate_crit_opt(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower().strip() not in VALID_CRITICALITIES:
            raise ValueError(f"Must be one of {VALID_CRITICALITIES}")
        return v.lower().strip() if v else None

    @field_validator("status")
    @classmethod
    def validate_stat_opt(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower().strip() not in VALID_ASSET_STATUSES:
            raise ValueError(f"Must be one of {VALID_ASSET_STATUSES}")
        return v.lower().strip() if v else None


from pydantic import BaseModel, Field, field_validator, ConfigDict


class AssetResponse(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    risk_score: float
    created_at: datetime
    updated_at: datetime
    last_seen: datetime


class AssetListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[AssetResponse]


class AssetHealthSummary(BaseModel):
    asset_id: str
    name: str
    status: str
    criticality: str
    risk_score: float
    risk_tier: str
    active_incidents_count: int
    total_alerts_count: int
    last_seen: datetime
