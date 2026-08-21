"""
tests/unit/test_phase27_kspm.py
===============================
Phase 27 Kubernetes Security Posture Management (KSPM) Unit Tests.
"""

import pytest
from backend.app.services.kubernetes_security_service import KubernetesSecurityService


class TestKSPMWorkloadAuditing:
    """Unit tests for Kubernetes manifest auditing and Pod Security Standards."""

    def test_privileged_manifest_flagged(self):
        """Manifest with privileged: true must fail compliance."""
        yaml_content = """
        apiVersion: v1
        kind: Pod
        metadata:
          name: test-pod
        spec:
          containers:
          - name: app
            image: nginx
            securityContext:
              privileged: true
        """
        res = KubernetesSecurityService.audit_manifest_content(yaml_content)
        assert res["is_compliant"] is False
        assert res["critical_violations"] >= 1
        assert res["workload_security_score"] < 100

    def test_secure_manifest_passes_compliance(self):
        """Compliant manifest with readOnlyRootFilesystem passes with 100 score."""
        yaml_content = """
        apiVersion: v1
        kind: Pod
        metadata:
          name: test-pod
        spec:
          containers:
          - name: app
            image: nginx:alpine
            securityContext:
              privileged: false
              readOnlyRootFilesystem: true
        """
        res = KubernetesSecurityService.audit_manifest_content(yaml_content)
        assert res["is_compliant"] is True
        assert res["violations_count"] == 0
        assert res["workload_security_score"] == 100
