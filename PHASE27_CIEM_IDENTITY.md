# PHASE 27 — CIEM IDENTITY & PRIVILEGE ESCALATION ANALYSIS

## 1. CIEM Threat Vectors

1. **`iam:PassRole` + `ec2:RunInstances`**: Enables attackers with minimal permissions to launch an EC2 instance with high-privilege IAM roles.
2. **`iam:CreatePolicyVersion`**: Allows non-admin identities to elevate themselves by updating policy definitions to `AdministratorAccess`.
3. **`sts:AssumeRole` Chaining**: Multi-hop role assumption leading to cross-account administrative takeover.
