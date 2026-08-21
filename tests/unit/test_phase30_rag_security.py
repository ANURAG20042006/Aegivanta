"""
tests/unit/test_phase30_rag_security.py
=======================================
Phase 30 RAG & Vector Database Security Unit Tests.
"""

import pytest
from backend.app.models.llm_security import VectorDBAuditRecord


class TestRAGSecurity:
    """Unit tests for vector database security audits and poisoning metrics."""

    def test_vectordb_audit_model_initialization(self):
        """VectorDBAuditRecord must store DB type, isolation status, and poisoning score."""
        audit = VectorDBAuditRecord(
            tenant_id="tenant-123",
            db_type="CHROMA_DB",
            collection_name="enterprise_kb_rag_index",
            total_embeddings_count=28400,
            is_tenant_isolated=True,
            has_unencrypted_embeddings=False,
            pii_exposure_detected=False,
            poisoning_anomaly_score=0.02,
            audit_status="SECURE"
        )
        assert audit.db_type == "CHROMA_DB"
        assert audit.is_tenant_isolated is True
        assert audit.audit_status == "SECURE"
