"""
tests/unit/test_phase3_3_k8s_runtime_validation.py
==================================================
Unit tests verifying all Kubernetes runtime validation tools.
Tests machine-readable outputs, missing CLI/cluster handling, error safety guards,
and secret hygiene across all validation scripts.
"""

import sys
import unittest.mock as mock
import pytest
from pathlib import Path

from scripts.preflight_kubernetes import check_kubernetes_preflight
from scripts.validate_k8s_live import run_live_validation
from scripts.smoke_test_k8s_api import run_smoke_test
from scripts.validate_k8s_hpa import validate_hpa
from scripts.test_k8s_worker_recovery import run_worker_recovery_test
from scripts.validate_k8s_ingress import validate_ingress
from scripts.validate_k8s_networkpolicy import validate_network_policy_enforcement


def test_preflight_missing_kubectl_returns_blocked():
    """Verify preflight returns BLOCKED when kubectl binary is missing."""
    with mock.patch("shutil.which", return_value=None):
        status, report = check_kubernetes_preflight()
        assert status == "BLOCKED"
        assert report["kubectl_installed"] is False
        assert "not installed" in report["reason"]


def test_preflight_missing_context_returns_blocked():
    """Verify preflight returns BLOCKED when no active context exists."""
    with mock.patch("shutil.which", return_value="/usr/bin/kubectl"):
        with mock.patch("subprocess.run") as mock_run:
            # version succeeds, current-context fails
            mock_run.side_effect = [
                mock.MagicMock(returncode=0, stdout='{"clientVersion": {"gitVersion": "v1.28.0"}}'),
                mock.MagicMock(returncode=1, stdout=""),
            ]
            status, report = check_kubernetes_preflight()
            assert status == "BLOCKED"
            assert "No active Kubernetes context" in report["reason"]


def test_preflight_auth_failure_returns_fail():
    """Verify preflight returns FAIL on cluster authentication failure."""
    with mock.patch("shutil.which", return_value="/usr/bin/kubectl"):
        with mock.patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                mock.MagicMock(returncode=0, stdout='{"clientVersion": {"gitVersion": "v1.28.0"}}'),
                mock.MagicMock(returncode=0, stdout="sentinelai-context"),
                mock.MagicMock(returncode=1, stderr="error: You must be logged in to the server (Unauthorized)"),
            ]
            status, report = check_kubernetes_preflight()
            assert status == "FAIL"
            assert "authentication failed" in report["reason"]


def test_preflight_success_returns_pass():
    """Verify preflight returns PASS when cluster and context are valid."""
    with mock.patch("shutil.which", return_value="/usr/bin/kubectl"):
        with mock.patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                mock.MagicMock(returncode=0, stdout='{"clientVersion": {"gitVersion": "v1.28.0"}}'),
                mock.MagicMock(returncode=0, stdout="sentinelai-context"),
                mock.MagicMock(returncode=0, stdout="Kubernetes control plane is running at https://127.0.0.1:6443"),
            ]
            status, report = check_kubernetes_preflight()
            assert status == "PASS"
            assert report["api_server_reachable"] is True


def test_validate_k8s_live_missing_kubectl_returns_blocked():
    """Verify live server-side validation returns exit code 2 (BLOCKED) without kubectl."""
    with mock.patch("shutil.which", return_value=None):
        code = run_live_validation()
        assert code == 2


def test_smoke_test_unreachable_api_returns_blocked():
    """Verify API smoke test returns exit code 2 (BLOCKED) when endpoint is unreachable."""
    code = run_smoke_test("http://127.0.0.1:59999")  # Unused port
    assert code == 2


def test_hpa_missing_metrics_server_returns_blocked():
    """Verify HPA validator returns BLOCKED (2) when metrics-server APIService is missing."""
    with mock.patch("shutil.which", return_value="/usr/bin/kubectl"):
        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.MagicMock(returncode=1, stderr="the server could not find the requested resource")
            code = validate_hpa("sentinelai")
            assert code == 2


@pytest.mark.asyncio
async def test_worker_recovery_production_refusal():
    """Verify worker recovery test refuses to execute on production without explicit chaos flag."""
    code = await run_worker_recovery_test(namespace="sentinelai", environment="production", allow_chaos=False)
    assert code == 1


def test_ingress_unresolvable_host_returns_blocked():
    """Verify ingress validator returns BLOCKED (2) for unresolvable DNS hostnames."""
    code = validate_ingress("non-existent-cluster-host-9999.invalid")
    assert code == 2


def test_networkpolicy_missing_kubectl_returns_blocked():
    """Verify NetworkPolicy validator returns BLOCKED (2) without kubectl."""
    with mock.patch("shutil.which", return_value=None):
        code = validate_network_policy_enforcement("sentinelai")
        assert code == 2
