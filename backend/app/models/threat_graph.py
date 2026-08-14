"""
backend/app/models/threat_graph.py
==================================
SQLAlchemy Models for Threat Intelligence Graph (Nodes & Evidence-Backed Edges).
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey, Index
from backend.app.database import Base


class ThreatGraphNode(Base):
    """Represents an entity node in the SOC Threat Intelligence Graph."""
    __tablename__ = "threat_graph_nodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    node_type = Column(String(50), nullable=False, index=True)  # ASSET, ALERT, IOC, INCIDENT, CAMPAIGN, TECHNIQUE, IP, DOMAIN
    reference_id = Column(String(255), nullable=True, index=True)  # Underlying primary key or unique identifier
    label = Column(String(255), nullable=False, index=True)
    properties = Column(JSON, nullable=True)  # Contextual attributes
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ThreatGraphEdge(Base):
    """Represents an evidence-backed directed relationship edge between two nodes."""
    __tablename__ = "threat_graph_edges"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_node_id = Column(String, ForeignKey("threat_graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_node_id = Column(String, ForeignKey("threat_graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False, index=True)  # TARGETS, CONTAINS, INDICATES, CORRELATED_WITH, EXECUTES, COMMUNICATES_WITH
    confidence = Column(Float, default=1.0, nullable=False)  # 0.0 - 1.0
    evidence_count = Column(Integer, default=1, nullable=False)  # Minimum 1 evidence item required
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    metadata_json = Column(JSON, nullable=True)  # Evidence references and supporting proof IDs

    __table_args__ = (
        Index("ix_threat_edge_source_target", "source_node_id", "target_node_id", "relationship_type"),
    )
