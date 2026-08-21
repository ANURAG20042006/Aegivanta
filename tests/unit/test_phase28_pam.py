"""
tests/unit/test_phase28_pam.py
==============================
Phase 28 Privileged Access Management (PAM) Unit Tests.
"""

import pytest
from backend.app.models.identity import PAMSessionElevation


class TestPAMJITElevations:
    """Unit tests for PAM Just-in-Time elevation lifecycle."""

    def test_pam_model_initialization(self):
        """PAMSessionElevation model must initialize with valid time boundaries and justification."""
        elevation = PAMSessionElevation(
            tenant_id="tenant-123",
            user_id="usr-456",
            username="sarah.connor@aegivanta.io",
            target_role="CLUSTER_ADMIN",
            target_resource="PROD_K8S_PRIMARY",
            justification="Emergency production bugfix",
            duration_minutes=60,
            status="PENDING"
        )
        assert elevation.target_role == "CLUSTER_ADMIN"
        assert elevation.duration_minutes == 60
        assert elevation.status == "PENDING"
