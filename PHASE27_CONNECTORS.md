# PHASE 27 — MULTI-CLOUD CONNECTORS REFERENCE

## 1. Supported Providers

| Provider | Authentication Method | Encrypted Storage |
|----------|-----------------------|-------------------|
| **AWS** | Cross-Account IAM AssumeRole with External ID | Fernet AES-256 Symmetric Key |
| **Azure** | Entra ID Service Principal (Client ID & Secret) | Fernet AES-256 Symmetric Key |
| **GCP** | Service Account Key JSON | Fernet AES-256 Symmetric Key |
| **Kubernetes** | In-Cluster Pod Service Account / Kubeconfig | Fernet AES-256 Symmetric Key |
