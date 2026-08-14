"""
backend/app/models/attack_coverage.py
=====================================
SQLAlchemy Models for MITRE ATT&CK Matrix Detection Coverage Snapshots.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime
from backend.app.database import Base


class AttackCoverageSnapshot(Base):
    """Stores historical and current snapshots of MITRE ATT&CK detection matrix coverage."""
    __tablename__ = "attack_coverage_snapshots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    observed_techniques_count = Column(Integer, default=0, nullable=False)
    detected_techniques_count = Column(Integer, default=0, nullable=False)
    total_matrix_techniques = Column(Integer, default=193, nullable=False)
    coverage_percentage = Column(Float, default=0.0, nullable=False)
    tactic_breakdown = Column(JSON, nullable=True)  # Coverage per tactic: Recon, Execution, Impact, etc.
    technique_details = Column(JSON, nullable=True)  # Details of covered vs observed techniques
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
