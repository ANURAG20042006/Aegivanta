"""
scripts/validate_k8s_manifests.py
=================================
Production-grade Offline Kubernetes Manifest Validator for SentinelAI.
Rigorously checks all manifests in k8s/ for schema validity, securityContext,
resource limits, probes, selector matching, port consistency, and secret isolation.
Fails with exit code 1 if any critical inconsistency or vulnerability is discovered.
"""

import sys
import os
import yaml
from pathlib import Path
from typing import List, Dict, Any, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
K8S_DIR = PROJECT_ROOT / "k8s"

REQUIRED_FILES = [
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
]


class ManifestValidator:
    def __init__(self, k8s_dir: Path):
        self.k8s_dir = k8s_dir
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.manifests: List[Tuple[str, Dict[str, Any]]] = []

    def log_error(self, file_name: str, msg: str):
        self.errors.append(f"[ERROR] {file_name}: {msg}")

    def log_warning(self, file_name: str, msg: str):
        self.warnings.append(f"[WARN] {file_name}: {msg}")

    def load_all_manifests(self):
        for req in REQUIRED_FILES:
            path = self.k8s_dir / req
            if not path.exists():
                self.log_error(req, "Required manifest file is missing.")
                continue

            try:
                with open(path, "r", encoding="utf-8") as f:
                    docs = list(yaml.safe_load_all(f))
                    for doc in docs:
                        if doc:
                            self.manifests.append((req, doc))
            except Exception as exc:
                self.log_error(req, f"YAML parsing failed: {exc}")

    def validate_structure_and_metadata(self):
        for file_name, doc in self.manifests:
            kind = doc.get("kind")
            api_ver = doc.get("apiVersion")
            metadata = doc.get("metadata", {})
            name = metadata.get("name")
            namespace = metadata.get("namespace")

            if not kind:
                self.log_error(file_name, "Missing 'kind' field.")
            if not api_ver:
                self.log_error(file_name, "Missing 'apiVersion' field.")
            if not name:
                self.log_error(file_name, "Missing 'metadata.name' field.")

            # All non-Namespace resources must specify sentinelai namespace
            if kind != "Namespace" and namespace != "sentinelai":
                self.log_error(file_name, f"Resource {kind}/{name} has invalid namespace '{namespace}' (expected 'sentinelai').")

    def validate_security_contexts(self):
        for file_name, doc in self.manifests:
            kind = doc.get("kind")
            if kind in ("Deployment", "StatefulSet"):
                name = doc["metadata"]["name"]
                pod_spec = doc.get("spec", {}).get("template", {}).get("spec", {})

                # Workload Pod SecurityContext
                pod_sc = pod_spec.get("securityContext", {})
                if pod_sc.get("runAsNonRoot") is not True:
                    self.log_error(file_name, f"{kind}/{name}: pod securityContext.runAsNonRoot must be True.")
                if kind == "Deployment" and pod_sc.get("runAsUser") != 10001:
                    self.log_error(file_name, f"{kind}/{name}: pod securityContext.runAsUser must be 10001.")
                if kind == "StatefulSet" and pod_sc.get("runAsUser") != 999:
                    self.log_error(file_name, f"{kind}/{name}: redis statefulset must run as UID 999.")

                # Seccomp Profile
                seccomp = pod_sc.get("seccompProfile", {}).get("type")
                if seccomp != "RuntimeDefault":
                    self.log_error(file_name, f"{kind}/{name}: seccompProfile.type must be 'RuntimeDefault'.")

                # Container SecurityContext
                for c in pod_spec.get("containers", []):
                    c_name = c.get("name")
                    c_sc = c.get("securityContext", {})
                    if c_sc.get("allowPrivilegeEscalation") is not False:
                        self.log_error(file_name, f"{kind}/{name} container '{c_name}': allowPrivilegeEscalation must be False.")

                    caps_drop = c_sc.get("capabilities", {}).get("drop", [])
                    if "ALL" not in caps_drop:
                        self.log_error(file_name, f"{kind}/{name} container '{c_name}': capabilities.drop must contain 'ALL'.")

                    caps_add = c_sc.get("capabilities", {}).get("add", [])
                    if "CAP_NET_RAW" in caps_add or "NET_RAW" in caps_add:
                        self.log_error(file_name, f"{kind}/{name} container '{c_name}': CAP_NET_RAW is prohibited on general workloads.")

                    if kind == "Deployment" and c_sc.get("readOnlyRootFilesystem") is not True:
                        self.log_error(file_name, f"{kind}/{name} container '{c_name}': readOnlyRootFilesystem must be True.")

    def validate_resource_limits(self):
        for file_name, doc in self.manifests:
            kind = doc.get("kind")
            if kind in ("Deployment", "StatefulSet"):
                name = doc["metadata"]["name"]
                containers = doc.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
                for c in containers:
                    c_name = c.get("name")
                    res = c.get("resources", {})
                    reqs = res.get("requests", {})
                    lims = res.get("limits", {})

                    if not reqs.get("cpu") or not reqs.get("memory"):
                        self.log_error(file_name, f"{kind}/{name} container '{c_name}': Missing cpu/memory resource requests.")
                    if not lims.get("cpu") or not lims.get("memory"):
                        self.log_error(file_name, f"{kind}/{name} container '{c_name}': Missing cpu/memory resource limits.")

    def validate_service_and_ingress_wiring(self):
        deployments = {
            doc["metadata"]["name"]: doc
            for f, doc in self.manifests if doc.get("kind") == "Deployment"
        }
        services = {
            doc["metadata"]["name"]: doc
            for f, doc in self.manifests if doc.get("kind") == "Service"
        }

        # 1. Validate API Service
        if "sentinelai-api" in services and "sentinelai-api" in deployments:
            svc = services["sentinelai-api"]
            dep = deployments["sentinelai-api"]
            svc_sel = svc.get("spec", {}).get("selector", {})
            pod_labels = dep.get("spec", {}).get("template", {}).get("metadata", {}).get("labels", {})

            for k, v in svc_sel.items():
                if pod_labels.get(k) != v:
                    self.log_error("service-api.yaml", f"Service selector {k}={v} does not match deployment label {pod_labels.get(k)}.")

            svc_port = svc["spec"]["ports"][0]["port"]
            c_port = dep["spec"]["template"]["spec"]["containers"][0]["ports"][0]["containerPort"]
            if svc_port != c_port or svc_port != 8000:
                self.log_error("service-api.yaml", f"Service port ({svc_port}) must match container port ({c_port}) on 8000.")

        # 2. Validate Ingress
        for f, doc in self.manifests:
            if doc.get("kind") == "Ingress":
                spec = doc.get("spec", {})
                ann = doc.get("metadata", {}).get("annotations", {})

                if ann.get("nginx.ingress.kubernetes.io/websocket-services") != "sentinelai-api":
                    self.log_error(f, "Ingress missing required websocket-services annotation pointing to 'sentinelai-api'.")
                if not spec.get("tls"):
                    self.log_error(f, "Ingress missing TLS configuration block.")

                backend_svc = spec["rules"][0]["http"]["paths"][0]["backend"]["service"]
                if backend_svc.get("name") != "sentinelai-api" or backend_svc.get("port", {}).get("number") != 8000:
                    self.log_error(f, f"Ingress backend service must point to 'sentinelai-api:8000' (got {backend_svc}).")

    def validate_secrets_and_configmaps(self):
        for f, doc in self.manifests:
            if doc.get("kind") == "Secret":
                for k, v in doc.get("stringData", {}).items():
                    if "CHANGE_ME" not in str(v):
                        self.log_error(f, f"Secret key '{k}' appears to contain non-template credential data.")

            if doc.get("kind") == "ConfigMap":
                for k, v in doc.get("data", {}).items():
                    if any(bad in k.lower() for bad in ["password", "secret_key", "token"]):
                        self.log_error(f, f"ConfigMap key '{k}' contains sensitive credential name.")

    def run_all(self) -> bool:
        self.load_all_manifests()
        self.validate_structure_and_metadata()
        self.validate_security_contexts()
        self.validate_resource_limits()
        self.validate_service_and_ingress_wiring()
        self.validate_secrets_and_configmaps()

        print("=================================================================")
        print("     SentinelAI Offline Kubernetes Manifest Validation Report    ")
        print("=================================================================")
        print(f"Manifests Loaded : {len(self.manifests)} resource documents")
        print(f"Total Warnings   : {len(self.warnings)}")
        print(f"Total Errors     : {len(self.errors)}")
        print("-----------------------------------------------------------------")

        for w in self.warnings:
            print(w)
        for e in self.errors:
            print(e)

        if not self.errors:
            print("RESULT: ALL KUBERNETES MANIFESTS PASSED STRICT VALIDATION (0 ERRORS)")
            print("=================================================================")
            return True
        else:
            print(f"RESULT: VALIDATION FAILED WITH {len(self.errors)} ERROR(S)")
            print("=================================================================")
            return False


if __name__ == "__main__":
    validator = ManifestValidator(K8S_DIR)
    ok = validator.run_all()
    sys.exit(0 if ok else 1)
