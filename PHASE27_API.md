# PHASE 27 — CNAPP API REFERENCE

## 1. Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/cloud-security/cnapp/summary` | Consolidated 0–100 CNAPP Posture Score & Breakdown. |
| `GET` | `/api/v1/cloud-security/accounts` | List connected AWS, Azure, GCP & K8s accounts. |
| `POST` | `/api/v1/cloud-security/accounts` | Onboard new cloud account with encrypted credentials. |
| `POST` | `/api/v1/cloud-security/accounts/{id}/sync` | Trigger live multi-cloud asset discovery sync. |
| `GET` | `/api/v1/cloud-security/cwpp/findings` | Active runtime threat detections across VMs/Pods. |
| `POST` | `/api/v1/cloud-security/cwpp/simulate-threat` | Simulate CWPP workload threat detection. |
| `POST` | `/api/v1/cloud-security/cwpp/contain/{id}` | Quarantine compromised workload. |
| `GET` | `/api/v1/cloud-security/serverless/findings` | List serverless function risks & overprivileged roles. |
| `POST` | `/api/v1/cloud-security/serverless/audit` | Audit serverless configuration. |
| `GET` | `/api/v1/cloud-security/k8s/clusters` | List Kubernetes clusters with KSPM health score. |
| `POST` | `/api/v1/cloud-security/k8s/clusters/enroll` | Enroll Kubernetes cluster into KSPM monitoring. |
| `GET` | `/api/v1/cloud-security/inventory` | Multi-cloud unified asset inventory. |
| `POST` | `/api/v1/cloud-security/cspm/scan` | Run CSPM compliance scan. |
| `GET` | `/api/v1/cloud-security/cspm/findings` | Open CSPM findings. |
| `POST` | `/api/v1/cloud-security/containers/scan` | Scan container image for CVEs and generate SBOM. |
| `GET` | `/api/v1/cloud-security/iam/analysis` | CIEM entitlement risks and escalation vectors. |
| `GET` | `/api/v1/cloud-security/attack-paths` | Synthesized attack path graphs. |
