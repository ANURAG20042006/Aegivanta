"""
tests/unit/test_phase3_3_kubernetes_manifests.py
================================================
Unit tests verifying production Kubernetes manifests for SentinelAI.
Validates YAML structure, securityContext hardening, non-root execution,
resource limits, health probes, HPA, PDB, NetworkPolicy, and secret separation.
"""

from pathlib import Path
import yaml
import pytest

K8S_DIR = Path(__file__).resolve().parents[2] / "k8s"


def load_all_manifests():
    manifests = []
    for yaml_file in sorted(K8S_DIR.glob("*.yaml")):
        with open(yaml_file, "r", encoding="utf-8") as f:
            docs = yaml.safe_load_all(f)
            for doc in docs:
                if doc:
                    manifests.append((yaml_file.name, doc))
    return manifests


def test_manifest_files_exist_and_parse():
    """Verify all expected Kubernetes manifests exist and are valid YAML."""
    expected_files = {
        "namespace.yaml",
        "serviceaccount.yaml",
        "configmap.yaml",
        "secret-template.yaml",
        "deployment-api.yaml",
        "deployment-worker.yaml",
        "service-api.yaml",
        "redis.yaml",
        "ingress.yaml",
        "hpa.yaml",
        "pdb.yaml",
        "networkpolicy.yaml"
    }
    actual_files = {f.name for f in K8S_DIR.glob("*.yaml")}
    assert expected_files.issubset(actual_files), f"Missing manifests: {expected_files - actual_files}"

    manifests = load_all_manifests()
    assert len(manifests) >= 12


def test_api_and_worker_security_context_hardening():
    """Verify API and Worker deployments enforce strict non-root and dropped capabilities."""
    manifests = load_all_manifests()

    deployments = [doc for name, doc in manifests if doc.get("kind") == "Deployment"]
    assert len(deployments) >= 2

    for dep in deployments:
        dep_name = dep["metadata"]["name"]
        pod_spec = dep["spec"]["template"]["spec"]

        # Pod-level security context
        pod_sc = pod_spec.get("securityContext", {})
        assert pod_sc.get("runAsNonRoot") is True, f"{dep_name} must have runAsNonRoot: true"
        assert pod_sc.get("runAsUser") == 10001, f"{dep_name} must run as UID 10001"
        assert pod_sc.get("seccompProfile", {}).get("type") == "RuntimeDefault"

        # Container-level security context
        containers = pod_spec.get("containers", [])
        for c in containers:
            c_name = c["name"]
            c_sc = c.get("securityContext", {})
            assert c_sc.get("allowPrivilegeEscalation") is False, f"{c_name} must disable privilege escalation"
            assert c_sc.get("readOnlyRootFilesystem") is True, f"{c_name} must use read-only root filesystem"
            assert "ALL" in c_sc.get("capabilities", {}).get("drop", []), f"{c_name} must drop ALL capabilities"

            # Must NOT contain CAP_NET_RAW
            caps_add = c_sc.get("capabilities", {}).get("add", [])
            assert "CAP_NET_RAW" not in caps_add and "NET_RAW" not in caps_add, f"{c_name} must not have NET_RAW"


def test_resource_requests_and_limits():
    """Verify all container specs define explicit CPU and Memory requests and limits."""
    manifests = load_all_manifests()
    for name, doc in manifests:
        if doc.get("kind") in ("Deployment", "StatefulSet"):
            pod_spec = doc["spec"]["template"]["spec"]
            for c in pod_spec.get("containers", []):
                res = c.get("resources", {})
                assert "requests" in res, f"{doc['metadata']['name']}:{c['name']} missing resource requests"
                assert "limits" in res, f"{doc['metadata']['name']}:{c['name']} missing resource limits"
                assert "cpu" in res["requests"] and "memory" in res["requests"]
                assert "cpu" in res["limits"] and "memory" in res["limits"]


def test_health_probes_configured_on_api():
    """Verify API deployment configures liveness, readiness, and startup probes."""
    manifests = load_all_manifests()
    api_dep = next(doc for name, doc in manifests if doc.get("metadata", {}).get("name") == "sentinelai-api")
    container = api_dep["spec"]["template"]["spec"]["containers"][0]

    assert "startupProbe" in container
    assert "livenessProbe" in container
    assert "readinessProbe" in container

    assert container["readinessProbe"]["httpGet"]["path"] == "/api/v1/health/ready"
    assert container["livenessProbe"]["httpGet"]["path"] == "/health"


def test_hpa_and_pdb_configuration():
    """Verify HPA scales both API and Worker, and PDB guarantees minAvailable >= 1."""
    manifests = load_all_manifests()

    hpas = [doc for name, doc in manifests if doc.get("kind") == "HorizontalPodAutoscaler"]
    assert len(hpas) >= 2
    hpa_targets = {h["spec"]["scaleTargetRef"]["name"] for h in hpas}
    assert "sentinelai-api" in hpa_targets
    assert "sentinelai-worker" in hpa_targets

    pdbs = [doc for name, doc in manifests if doc.get("kind") == "PodDisruptionBudget"]
    assert len(pdbs) >= 2
    for pdb in pdbs:
        assert pdb["spec"].get("minAvailable") == 1


def test_network_policy_rules():
    """Verify NetworkPolicy specifies ingress and egress microsegmentation."""
    manifests = load_all_manifests()
    np = next(doc for name, doc in manifests if doc.get("kind") == "NetworkPolicy")

    assert "Ingress" in np["spec"]["policyTypes"]
    assert "Egress" in np["spec"]["policyTypes"]
    # Verify egress to Redis port 6379 and Postgres port 5432
    egress_ports = [
        port_spec["port"]
        for rule in np["spec"]["egress"]
        for port_spec in rule.get("ports", [])
    ]
    assert 6379 in egress_ports
    assert 5432 in egress_ports
