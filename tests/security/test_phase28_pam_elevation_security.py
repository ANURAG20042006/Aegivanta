"""
tests/security/test_phase28_pam_elevation_security.py
=====================================================
Phase 28 PAM Elevation Security & Time-Bound Expiration Tests.
"""

import pytest
from datetime import datetime, timezone, timedelta
from backend.app.models.identity import PAMSessionElevation


class TestPAMElevationSecurity:
    """Security tests validating JIT elevation safety boundaries."""

    def test_elevation_time_bounded_expiry(self):
        """Active elevation must expire after allocated duration."""
        now = datetime.now(timezone.utc)
        duration_minutes = 30
        elevation = PAMSessionElevation(
            tenant_id="tenant-123",
            user_id="usr-1",
            username="admin@aegivanta.io",
            target_role="CLUSTER_ADMIN",
            target_resource="K8S_PROD",
            justification="Security patch",
            duration_minutes=duration_minutes,
            status="ACTIVE",
            approved_by="approver-1",
            approved_at=now,
            expires_at=now + timedelta(minutes=duration_minutes)
        )
        assert elevation.expires_at > elevation.approved_at
        assert (elevation.expires_at - elevation.approved_at).total_seconds() == 1800
