# AEGIVANTA — PHASE 21 CLOUD & CONTAINER SECURITY ARCHITECTURE

## 1. Multi-Cloud & Container Security Fabric
Phase 21 provides unified Cloud Security Posture Management (CSPM), Kubernetes Security Posture Management (KSPM), Cloud Infrastructure Entitlement Management (CIEM), Container Image & SBOM security, and Graph-based Cloud Attack Path modeling.

```mermaid
graph TD
    subgraph Multi-Cloud Ingestion
        AWS[AWS EC2 / S3 / RDS / IAM]
        GCP[GCP Compute / CloudSQL / GCS]
        Azure[Azure VMs / Blob / Entra ID]
        K8s[Kubernetes Clusters & Workloads]
    end

    AWS --> CAI[Cloud Asset Inventory Engine]
    GCP --> CAI
    Azure --> CAI
    K8s --> CAI

    CAI --> CSPM[CSPM Rule Engine: CIS Benchmarks]
    CAI --> CIEM[CIEM IAM Risk & Escalation Engine]
    CAI --> KSPM[Kubernetes Workload Security Engine]
    
    IMG[Container Registry & Docker Images] --> CS[Container Security: CVE Scanner + SBOM + Cosign Signature Verifier]
    
    CSPM --> AG[Cloud Attack Path Graph Engine]
    CIEM --> AG
    KSPM --> AG
    CS --> AG
    
    AG --> UI[Cloud Security Command Center Dashboard]
```

## 2. Core Capabilities
- **Cloud Asset Inventory**: Discovers and normalizes multi-cloud assets across AWS, GCP, Azure, and Kubernetes.
- **CSPM Misconfiguration Detection**: Real-time auditing against CIS AWS/K8s benchmarks.
- **Container Vulnerability & SBOM Scanner**: CycloneDX SBOM generator, CVE matching with CVSS scoring, and Cosign image signature verification.
- **Kubernetes Workload Security**: Evaluates manifests for `privileged`, `hostNetwork`, dangerous capabilities, and plaintext credentials.
- **CIEM IAM Risk Analyzer**: Detects stale accounts, over-privileged wildcards, and multi-hop privilege escalation vectors.
- **Explainable Attack Path Graphs**: Models kill chains from Internet ingress to S3/DB exfiltration with prescriptive remediation sequences.
