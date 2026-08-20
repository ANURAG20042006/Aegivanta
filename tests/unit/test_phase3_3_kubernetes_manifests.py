"""
tests/unit/test_phase3_3_kubernetes_manifests.py
================================================
Unit tests verifying production Kubernetes manifests for SentinelAI.
Validates YAML structure, securityContext hardening, non-root execution,
resource limits, health probes, HPA, PDB, NetworkPolicy, secret separation,
Service/Ingress/Port alignment, and WebSocket upgrade configurations.
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
    """Verify HPA scales both API and Worker roles, and PDB guarantees minAvailable >= 1.
    Phase 3.11: HPAs are now per worker role (detection, response, threat-intel, hunting).
    The legacy 'sentinelai-worker' generic HPA has been replaced with role-specific HPAs.
    """
    manifests = load_all_manifests()

    hpas = [doc for name, doc in manifests if doc.get("kind") == "HorizontalPodAutoscaler"]
    assert len(hpas) >= 3, f"Expected >= 3 HPAs (API + worker roles), got {len(hpas)}"
    hpa_targets = {h["spec"]["scaleTargetRef"]["name"] for h in hpas}
    assert "sentinelai-api" in hpa_targets

    # Phase 3.11: at least one worker role HPA must be present
    worker_hpa_targets = {t for t in hpa_targets if "worker" in t}
    assert len(worker_hpa_targets) >= 1, \
        f"Expected at least 1 worker-role HPA, got: {hpa_targets}"

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


def test_service_selector_and_port_matching():
    """Verify Service selectors match Deployment labels and container ports match."""
    manifests = load_all_manifests()
    api_svc = next(doc for name, doc in manifests if doc.get("kind") == "Service" and doc.get("metadata", {}).get("name") == "sentinelai-api")
    api_dep = next(doc for name, doc in manifests if doc.get("kind") == "Deployment" and doc.get("metadata", {}).get("name") == "sentinelai-api")

    svc_selector = api_svc["spec"]["selector"]
    pod_labels = api_dep["spec"]["template"]["metadata"]["labels"]
    for k, v in svc_selector.items():
        assert pod_labels.get(k) == v, f"Selector {k}={v} does not match pod label"

    svc_port = api_svc["spec"]["ports"][0]["port"]
    container_port = api_dep["spec"]["template"]["spec"]["containers"][0]["ports"][0]["containerPort"]
    assert svc_port == container_port == 8000


def test_ingress_service_and_websocket_annotation_matching():
    """Verify Ingress rules target sentinelai-api on port 8000 and include websocket annotations."""
    manifests = load_all_manifests()
    ingress = next(doc for name, doc in manifests if doc.get("kind") == "Ingress")

    annotations = ingress["metadata"].get("annotations", {})
    assert annotations.get("nginx.ingress.kubernetes.io/websocket-services") == "sentinelai-api"
    assert annotations.get("nginx.ingress.kubernetes.io/ssl-redirect") == "true"

    rule = ingress["spec"]["rules"][0]
    backend = rule["http"]["paths"][0]["backend"]["service"]
    assert backend["name"] == "sentinelai-api"
    assert backend["port"]["number"] == 8000


def test_serviceaccount_automount_token_disabled():
    """Verify ServiceAccount explicitly disables automatic API credential mounting."""
    manifests = load_all_manifests()
    sa = next(doc for name, doc in manifests if doc.get("kind") == "ServiceAccount")
    assert sa.get("automountServiceAccountToken") is False


def test_secret_template_zero_plaintext_credentials():
    """Verify secret-template contains only CHANGE_ME_* placeholder values."""
    manifests = load_all_manifests()
    secret = next(doc for name, doc in manifests if doc.get("kind") == "Secret")
    data = secret.get("stringData", {})

    for key, val in data.items():
        assert "CHANGE_ME" in str(val), f"Secret {key} contains potentially non-template value"


def test_secret_and_configmap_references_valid():
    """Verify API and Worker deployments reference valid ConfigMap and Secret names."""
    manifests = load_all_manifests()
    deployments = [doc for name, doc in manifests if doc.get("kind") == "Deployment"]

    for dep in deployments:
        c = dep["spec"]["template"]["spec"]["containers"][0]
        env_from = c.get("envFrom", [])
        cm_names = [e["configMapRef"]["name"] for e in env_from if "configMapRef" in e]
        sec_names = [e["secretRef"]["name"] for e in env_from if "secretRef" in e]

        assert "sentinelai-config" in cm_names
        assert "sentinelai-secrets" in sec_names
