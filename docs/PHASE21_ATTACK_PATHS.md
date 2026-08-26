# AEGIVANTA — PHASE 21 CLOUD ATTACK PATH GRAPH ANALYSIS

## 1. Multi-Hop Graph Traversal
Connects disparate cloud layers into unified attack paths:
1. **Initial Access**: Internet-exposed Application Load Balancer or ingress controller.
2. **Execution / Lateral Movement**: Vulnerable Kubernetes Pod (e.g. `CVE-2024-21626`).
3. **Privilege Escalation**: Over-privileged IAM role assumed by node or workload.
4. **Data Impact / Exfiltration**: Direct read/dump of unencrypted customer financial storage buckets.

## 2. Prescriptive Remediation Sequencing
Provides ordered fix instructions to break attack paths at the lowest-friction defensive gate.
