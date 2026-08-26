# PHASE 27 — KSPM GOVERNANCE & POD SECURITY STANDARDS

## 1. Kubernetes Security Standards

1. **Privileged Containers**: Strictly disallowed in production namespaces.
2. **Namespace Isolation**: `hostNetwork`, `hostPID`, and `hostIPC` must be disabled.
3. **Capabilities**: Drop `ALL` capabilities and whitelist only least-privilege essentials (e.g. `NET_BIND_SERVICE`).
4. **Filesystem**: Enforce `readOnlyRootFilesystem: true` with volume mounts for ephemeral temp directories.
