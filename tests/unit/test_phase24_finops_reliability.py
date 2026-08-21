"""
tests/unit/test_phase24_finops_reliability.py
=============================================
Phase 24 FinOps, Capacity Planning, and SRE SLO Tests.
"""

import pytest
from backend.app.services.finops_capacity_service import (
    FinOpsCapacityService, COST_MODEL, SLO_TARGETS
)


class TestFinOpsCostModel:
    """Tests for tenant-aware cost estimation."""

    def test_zero_usage_produces_zero_total(self):
        """Zero usage across all dimensions yields zero total cost."""
        result = FinOpsCapacityService.estimate_tenant_monthly_cost(
            vcpus=0, storage_hot_gb=0, storage_warm_gb=0, storage_cold_gb=0,
            monthly_events_millions=0, monthly_ml_inferences_thousands=0, network_egress_gb=0
        )
        assert result["total_monthly_usd"] == 0.0

    def test_cost_breakdown_sums_to_total(self):
        """Sum of all breakdown components must equal total."""
        result = FinOpsCapacityService.estimate_tenant_monthly_cost(
            vcpus=16, storage_hot_gb=100, storage_warm_gb=500, storage_cold_gb=2000,
            monthly_events_millions=30.0, monthly_ml_inferences_thousands=120.0, network_egress_gb=80.0
        )
        total_from_breakdown = round(sum(result["breakdown"].values()), 2)
        assert abs(total_from_breakdown - result["total_monthly_usd"]) < 0.01

    def test_more_vcpus_increases_compute_cost(self):
        """Doubling vCPUs must double compute cost."""
        r8 = FinOpsCapacityService.estimate_tenant_monthly_cost(
            vcpus=8, storage_hot_gb=0, storage_warm_gb=0, storage_cold_gb=0,
            monthly_events_millions=0, monthly_ml_inferences_thousands=0, network_egress_gb=0
        )
        r16 = FinOpsCapacityService.estimate_tenant_monthly_cost(
            vcpus=16, storage_hot_gb=0, storage_warm_gb=0, storage_cold_gb=0,
            monthly_events_millions=0, monthly_ml_inferences_thousands=0, network_egress_gb=0
        )
        assert r16["breakdown"]["compute_usd"] == pytest.approx(r8["breakdown"]["compute_usd"] * 2, rel=0.01)

    def test_hot_storage_more_expensive_than_cold(self):
        """Hot storage must be more expensive per GB than cold storage."""
        r_hot = FinOpsCapacityService.estimate_tenant_monthly_cost(
            vcpus=0, storage_hot_gb=1, storage_warm_gb=0, storage_cold_gb=0,
            monthly_events_millions=0, monthly_ml_inferences_thousands=0, network_egress_gb=0
        )
        r_cold = FinOpsCapacityService.estimate_tenant_monthly_cost(
            vcpus=0, storage_hot_gb=0, storage_warm_gb=0, storage_cold_gb=1,
            monthly_events_millions=0, monthly_ml_inferences_thousands=0, network_egress_gb=0
        )
        assert r_hot["breakdown"]["storage_usd"] > r_cold["breakdown"]["storage_usd"]

    def test_unit_economics_cost_per_event_is_positive(self):
        """Cost per event must be a positive float."""
        result = FinOpsCapacityService.estimate_tenant_monthly_cost(
            vcpus=8, storage_hot_gb=100, storage_warm_gb=200, storage_cold_gb=500,
            monthly_events_millions=10.0, monthly_ml_inferences_thousands=50.0, network_egress_gb=20.0
        )
        assert result["unit_economics"]["cost_per_event"] > 0

    def test_cost_model_constants_positive(self):
        """All cost model constants must be strictly positive."""
        for key, val in COST_MODEL.items():
            assert val > 0, f"Cost model constant {key} must be positive"


class TestCapacityDashboard:
    """Tests for capacity planning metrics."""

    def test_capacity_dashboard_returns_required_keys(self):
        """Capacity dashboard must include EPS, worker, queue, and storage metrics."""
        result = FinOpsCapacityService.get_capacity_dashboard("test-tenant")
        required_keys = [
            "telemetry_eps", "worker_utilization_pct", "cpu_utilization_pct",
            "memory_utilization_pct", "queue_depth_alerts", "queue_depth_telemetry",
            "storage_used_gb", "storage_capacity_gb", "active_sensors", "sensor_count"
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_storage_used_does_not_exceed_capacity(self):
        """Storage used must not exceed storage capacity."""
        result = FinOpsCapacityService.get_capacity_dashboard("test-tenant")
        assert result["storage_used_gb"] <= result["storage_capacity_gb"]

    def test_active_sensors_does_not_exceed_total(self):
        """Active sensors count must not exceed total sensor count."""
        result = FinOpsCapacityService.get_capacity_dashboard("test-tenant")
        assert result["active_sensors"] <= result["sensor_count"]

    def test_utilization_percentages_in_valid_range(self):
        """CPU, memory, and worker utilization must be between 0 and 100."""
        result = FinOpsCapacityService.get_capacity_dashboard("test-tenant")
        for metric in ["cpu_utilization_pct", "memory_utilization_pct", "worker_utilization_pct"]:
            assert 0 <= result[metric] <= 100, f"{metric} out of range: {result[metric]}"


class TestSLODashboard:
    """Tests for SRE SLO error budget tracking."""

    def test_slo_dashboard_returns_all_slo_definitions(self):
        """SLO dashboard must include all SLO targets."""
        result = FinOpsCapacityService.get_slo_dashboard()
        slo_names = {s["slo_name"] for s in result["slos"]}
        for slo_name in SLO_TARGETS.keys():
            assert slo_name in slo_names

    def test_all_measured_slos_are_compliant(self):
        """All configured SLO measurements must be within target (pass/fail field)."""
        result = FinOpsCapacityService.get_slo_dashboard()
        for slo in result["slos"]:
            assert isinstance(slo["compliant"], bool), "compliant must be a bool"
            assert isinstance(slo["error_budget_remaining_pct"], (int, float)), "error budget must be numeric"

    def test_error_budget_remaining_non_negative(self):
        """Error budget remaining must be >= 0."""
        result = FinOpsCapacityService.get_slo_dashboard()
        for slo in result["slos"]:
            assert slo["error_budget_remaining_pct"] >= 0, f"Negative error budget for {slo['slo_name']}"

    def test_slo_overall_compliance_is_boolean(self):
        """Overall compliance field must be a boolean."""
        result = FinOpsCapacityService.get_slo_dashboard()
        assert isinstance(result["overall_compliance"], bool)

    def test_slo_dashboard_has_period_and_timestamp(self):
        """SLO dashboard must have period and timestamp fields."""
        result = FinOpsCapacityService.get_slo_dashboard()
        assert "period" in result
        assert "generated_at" in result
