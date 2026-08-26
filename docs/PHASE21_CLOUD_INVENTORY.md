# AEGIVANTA — PHASE 21 CLOUD ASSET INVENTORY

## 1. Resource Normalization & Schema
Tracks:
- Virtual Machines (`VM` on AWS EC2, GCP GCE, Azure VM)
- Object Storage (`STORAGE_BUCKET` on S3, GCS, Azure Blob)
- Relational & NoSQL Databases (`DATABASE` on RDS, Aurora, CloudSQL)
- Kubernetes Objects (`K8S_POD`, `K8S_DEPLOYMENT`, `K8S_SERVICE`)
- IAM Entities (`IAM_ROLE`, `IAM_USER`, `SERVICE_ACCOUNT`)
- Network Ingress (`LOAD_BALANCER`, `ALB`, `INGRESS`)

## 2. Ingestion & Risk Scoring
Assigns dynamic risk scores based on asset exposure level (`PUBLIC_INGRESS` vs `INTERNAL`), attached IAM privilege scope, and detected CVEs.
