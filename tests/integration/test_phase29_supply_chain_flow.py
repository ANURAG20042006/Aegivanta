"""
tests/integration/test_phase29_supply_chain_flow.py
===================================================
Phase 29 Supply Chain & SBOM 2.0 Integration Flow Tests.
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


class TestSupplyChainIntegrationFlow:
    """Integration tests for SBOM, OpenVEX, and SLSA provenance APIs."""

    def test_sbom_vex_and_slsa_flow(self, client, auth_headers):
        """Test summary, SBOM components list, CycloneDX generation, VEX publishing, and SLSA verification."""
        # 1. Summary
        sum_resp = client.get("/api/v1/supply-chain/summary", headers=auth_headers)
        assert sum_resp.status_code == 200
        assert "overall_supply_chain_score" in sum_resp.json()

        # 2. SBOM Components & CycloneDX generation
        comp_resp = client.get("/api/v1/supply-chain/sbom/components", headers=auth_headers)
        assert comp_resp.status_code == 200
        assert len(comp_resp.json()) >= 1

        gen_resp = client.post(
            "/api/v1/supply-chain/sbom/generate",
            json={"format_type": "CYCLONEDX_1_5"},
            headers=auth_headers
        )
        assert gen_resp.status_code == 200
        assert gen_resp.json()["bomFormat"] == "CycloneDX"

        # 3. Publish OpenVEX statement
        vex_pub = client.post(
            "/api/v1/supply-chain/vex/publish",
            json={
                "vulnerability_id": "CVE-2026-9999",
                "product_purl": "pkg:npm/test-pkg@1.0.0",
                "status": "NOT_AFFECTED",
                "justification": "Non-reachable entrypoint",
                "impact_statement": "Protected by runtime sandbox"
            },
            headers=auth_headers
        )
        assert vex_pub.status_code == 200
        assert vex_pub.json()["status"] == "NOT_AFFECTED"

        # 4. SLSA Attestations
        att_resp = client.get("/api/v1/supply-chain/slsa/attestations", headers=auth_headers)
        assert att_resp.status_code == 200
        assert len(att_resp.json()) >= 1
