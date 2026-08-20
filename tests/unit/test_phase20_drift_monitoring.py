import pytest
from backend.app.database import AsyncSessionFactory, init_db
from backend.app.services.model_drift_monitoring_service import ModelDriftMonitoringService


def test_psi_calculation():
    # Identical distributions -> PSI ~ 0.0
    dist1 = [0.2, 0.2, 0.2, 0.2, 0.2]
    psi_stable = ModelDriftMonitoringService.calculate_psi(dist1, dist1)
    assert psi_stable == 0.0

    # Slightly shifted distribution -> PSI < 0.1
    dist_slight = [0.18, 0.22, 0.19, 0.21, 0.20]
    psi_slight = ModelDriftMonitoringService.calculate_psi(dist1, dist_slight)
    assert psi_slight < 0.1

    # Heavily shifted distribution -> PSI > 0.2
    dist_drifted = [0.05, 0.05, 0.10, 0.40, 0.40]
    psi_drifted = ModelDriftMonitoringService.calculate_psi(dist1, dist_drifted)
    assert psi_drifted > 0.2


@pytest.mark.asyncio
async def test_drift_and_quality_metrics_retrieval():
    await init_db()
    async with AsyncSessionFactory() as db:
        tenant_id = "test-tenant-p20-drift"

        drift_state = await ModelDriftMonitoringService.get_latest_drift_metrics(db, tenant_id)
        assert "overall_psi" in drift_state
        assert "drift_status" in drift_state
        assert "feature_drift_breakdown" in drift_state

        quality = await ModelDriftMonitoringService.get_detection_quality(db, tenant_id)
        assert quality["precision"] >= 0.90
        assert quality["f1_score"] >= 0.90
        assert quality["throughput_eps"] > 0
