import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.container_security_service import ContainerSecurityService


def test_cosign_signature_verification():
    valid = ContainerSecurityService.verify_cosign_signature("sha256:abc", "sig_valid_production_signer_2026")
    assert valid == "SIGNED_VALID"

    unsigned = ContainerSecurityService.verify_cosign_signature("sha256:abc", None)
    assert unsigned == "UNSIGNED"

    invalid = ContainerSecurityService.verify_cosign_signature("sha256:abc", "invalid_bad_key")
    assert invalid == "UNSIGNED"


def test_sbom_generation():
    sbom = ContainerSecurityService.generate_sbom_summary("aegivanta/backend:v21.0.0")
    assert sbom["format"] == "CycloneDX-1.5-JSON"
    assert sbom["components_count"] > 100
    assert len(sbom["runtime_packages"]) >= 4
    pkg_names = [p["name"] for p in sbom["runtime_packages"]]
    assert "fastapi" in pkg_names
    assert "sqlalchemy" in pkg_names


@pytest.mark.asyncio
async def test_container_image_scan():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p21-cnt"

        scan = await ContainerSecurityService.scan_container_image(
            db=db,
            tenant_id=tenant_id,
            image_name="aegivanta/vulnerable-app",
            image_tag="legacy-1.0",
            signature_token="sig_valid_key_sample"
        )
        assert scan["signature_status"] == "SIGNED_VALID"
        assert scan["critical_cve_count"] >= 1
        assert any(v["cve_id"] == "CVE-2024-21626" for v in scan["vulnerabilities"])

        scans = await ContainerSecurityService.list_image_scans(db, tenant_id)
        assert len(scans) >= 1
