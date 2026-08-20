# AEGIVANTA — PHASE 21 KUBERNETES SECURITY (KSPM)

## 1. PodSecurityStandards & Manifest Auditing
Audits Kubernetes YAML manifests against baseline and restricted profiles:
- `K8S-SEC-001`: `privileged: true` execution flags.
- `K8S-SEC-002`: `hostNetwork: true` namespace sharing.
- `K8S-SEC-003`: `hostPID: true` host process visibility.
- `K8S-SEC-004`: Dangerous Linux capabilities (`CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, `CAP_NET_RAW`).
- `K8S-SEC-005`: Plaintext API keys and database passwords hardcoded in environment blocks.
- `K8S-SEC-006`: Mutable container root filesystems.
