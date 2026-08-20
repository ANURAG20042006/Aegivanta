import pytest
from backend.app.services.kubernetes_security_service import KubernetesSecurityService


def test_k8s_manifest_audit_insecure_workload():
    insecure_yaml = """
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: insecure-worker
    spec:
      template:
        spec:
          hostNetwork: true
          hostPID: true
          containers:
          - name: worker
            image: worker:latest
            securityContext:
              privileged: true
              capabilities:
                add: ["CAP_SYS_ADMIN"]
            env:
            - name: API_KEY
              value: "super_secret_api_key_123"
    """

    res = KubernetesSecurityService.audit_manifest_content(insecure_yaml)
    assert res["is_compliant"] is False
    assert res["violations_count"] >= 4
    assert res["critical_violations"] >= 2
    rule_ids = [v["rule"] for v in res["violations"]]
    assert "K8S-SEC-001" in rule_ids # Privileged
    assert "K8S-SEC-002" in rule_ids # hostNetwork
    assert "K8S-SEC-004" in rule_ids # CAP_SYS_ADMIN
    assert "K8S-SEC-005" in rule_ids # Hardcoded secret
    assert res["workload_security_score"] < 50


def test_k8s_manifest_audit_hardened_workload():
    hardened_yaml = """
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: hardened-worker
    spec:
      template:
        spec:
          containers:
          - name: worker
            image: worker:latest
            securityContext:
              privileged: false
              readOnlyRootFilesystem: true
              allowPrivilegeEscalation: false
    """

    res = KubernetesSecurityService.audit_manifest_content(hardened_yaml)
    assert res["is_compliant"] is True
    assert res["violations_count"] == 0
    assert res["workload_security_score"] == 100
