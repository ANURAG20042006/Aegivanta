from typing import Literal, Optional
from pydantic import BaseModel, Field


class ReportGenerationRequest(BaseModel):
    """Payload for initiating a threat intelligence report export."""
    format: Literal["pdf", "excel", "csv"] = Field(..., json_schema_extra={"example": "pdf"})
    include_shap_charts: bool = Field(default=True)
    start_date: Optional[str] = Field(default=None, json_schema_extra={"example": "2026-08-01"})
    end_date: Optional[str] = Field(default=None, json_schema_extra={"example": "2026-08-05"})


class ReportResponse(BaseModel):
    """Response schema following report generation."""
    report_id: str
    file_name: str
    format: str
    download_url: str
    generated_at: str
    total_records_exported: int
