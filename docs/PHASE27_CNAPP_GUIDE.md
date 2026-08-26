# PHASE 27 — CNAPP OPERATIONS GUIDE

## 1. Multi-Pillar Posture Management

1. **CSPM Operations**:
   - Run periodic automated scans via `/api/v1/cloud-security/cspm/scan`.
   - Monitor CIS Benchmark compliance across S3, IAM, Security Groups, and RDS.
2. **CWPP Runtime Protection**:
   - Deploy eBPF sensors onto Kubernetes nodes and container hosts.
   - Detect and quarantine reverse shells, crypto-mining, and capability abuses.
3. **CIEM Identity Hardening**:
   - Audit IAM roles and access keys for dormant credentials and privilege escalation paths.
4. **KSPM Cluster Governance**:
   - Enforce Pod Security Standards: `RESTRICTED` in production namespaces.
