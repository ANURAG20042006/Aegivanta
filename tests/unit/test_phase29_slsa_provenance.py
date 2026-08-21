"""
tests/unit/test_phase29_slsa_provenance.py
==========================================
Phase 29 SLSA Level 3 Provenance & Attestation Unit Tests.
"""

import pytest
from backend.app.models.supply_chain import SLSAPipelineAttestation


class TestSLSAProvenance:
    """Unit tests for SLSA Level 3 builder isolation and provenance verification."""

    def test_slsa_attestation_model_fields(self):
        """SLSAPipelineAttestation must store builder ID, commit SHA, and Cosign signature."""
        att = SLSAPipelineAttestation(
            tenant_id="tenant-123",
            artifact_name="aegivanta-backend:v29.0.0",
            artifact_digest="sha256:4b91048b29c9a091e48bc894e7710fa929188a8b9e6f8a4e421c97a5b3a16709",
            slsa_level="SLSA_LEVEL_3",
            builder_id="https://github.com/actions/runner@v2",
            build_invocation_id="run-101",
            cosign_signature="MEUCIQ...",
            is_signature_verified=True,
            source_repo_uri="https://github.com/aegivanta/core",
            source_commit_sha="85f6a81b34c8920194821a4f02819bc482910482"
        )
        assert att.slsa_level == "SLSA_LEVEL_3"
        assert att.is_signature_verified is True
        assert att.source_commit_sha == "85f6a81b34c8920194821a4f02819bc482910482"
