"""
tests/integration/test_phase42_cluster_flow.py
==============================================
Phase 42 Multi-Region Cluster & Residency Boundaries Integration Tests.
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    password = os.getenv("SENTINEL_ADMIN_PASSWORD", "TestAdminPassword2026!")
    res = client.post("/api/v1/auth/login", data={"username": "admin", "password": password})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestMultiRegionClusterFlow:
    """Integration tests for multi-region summary, listing clusters, and residency boundaries."""

    def test_multi_region_cluster_flow(self, client, auth_headers):
        """Test summary, clusters, and creating a data residency boundary."""
        # 1. Summary
        sum_resp = client.get("/api/v1/multi-region/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_resilience_score" in sum_resp.json()

        # 2. List Clusters
        cls_resp = client.get("/api/v1/multi-region/clusters", headers=auth_headers)
        assert cls_resp.status_code == 200
        clusters = cls_resp.json()
        assert len(clusters) >= 1

        # 3. Create Residency Boundary
        bnd_resp = client.post(
            "/api/v1/multi-region/residency",
            json={
                "boundary_name": "Japanese APPI Sovereign Partition",
                "compliance_standard": "APPI_JAPAN",
                "enforced_regions": "AP_NORTHEAST_1,AP_NORTHEAST_3",
                "strict_egress_block": True
            },
            headers=auth_headers
        )
        assert bnd_resp.status_code == 200
        assert bnd_resp.json()["compliance_standard"] == "APPI_JAPAN"
